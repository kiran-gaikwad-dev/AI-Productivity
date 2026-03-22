from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import preprocessing
import models
import data_generator
import pandas as pd

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["ai_productivity"]
activity_logs = db["activity_logs"]
users_col = db["users"]

app = FastAPI(title="AI Productivity Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/seed")
def seed_database(background_tasks: BackgroundTasks):
    """
    Production-friendly endpoint to generate 1000 logs and retrain models.
    Essential for Render deployment where data_generator.py can't loop infinitely.
    """
    # Generate simulated logs
    batch = data_generator.generate_activity_batch(1000)
    
    # Insert safely into MongoDB
    activity_logs.insert_many(batch)
    
    # Run the window cleanup
    data_generator.clean_old_records(keep_limit=5000)
    
    # Train models synchronously for immediate use
    raw_data = list(activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10000))
    if raw_data:
        df = preprocessing.preprocess_data(raw_data)
        models.train_clustering(df)
        models.train_classification(df)
        
    return {
        "status": "success",
        "message": "1000 Synthetic records successfully generated, inserted, and models re-trained."
    }

app = FastAPI(title="AI Productivity Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/train")
def train_models():
    # Fetch recent logs for training to avoid OOM for a scalable system
    raw_data = list(activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10000))
    if not raw_data:
        return {"message": "No data available"}
        
    df = preprocessing.preprocess_data(raw_data)
    
    res_cluster = models.train_clustering(df)
    res_class = models.train_classification(df)
    
    return {"clustering": res_cluster, "classification": res_class}

@app.get("/predict/{user_id}")
def user_prediction(user_id: str):
    # Fetch recent user data
    raw_data = list(activity_logs.find({"user_id": user_id}, {"_id": 0}).sort("timestamp", -1).limit(500))
    if not raw_data:
        return {"error": "User not found or no data"}
        
    df = preprocessing.preprocess_data(raw_data)
    
    overall_score = models.calculate_productivity_score(df)
    
    # Predict user cluster based on their average behavior
    avg_features = {
        'hour_of_day': df['hour_of_day'].mean(),
        'duration': df['duration'].mean(),
        'tab_switch_rate': df['tab_switch_rate'].mean(),
        'notification_rate': df['notification_rate'].mean(),
    }
    
    cluster_profile = models.predict_cluster(avg_features)
    
    # Save the computed data to the user collection
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"cluster": cluster_profile, "productivity_score": overall_score}},
        upsert=True
    )
    
    return {
        "user_id": user_id,
        "cluster_profile": cluster_profile,
        "productivity_score": overall_score,
        "total_sessions": len(df)
    }

@app.get("/stats/global")
def get_global_stats():
    try:
        # Fetch recent global logs for aggregate statistics
        raw_data = list(activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10000))
        if not raw_data:
            return {"message": "No data available"}
            
        df = preprocessing.preprocess_data(raw_data)
        
        # Calculate exactly how many minutes are pure focus vs distractions
        total_time = df['duration'].sum()
        productive_time = df[df['is_distracting'] == 0]['duration'].sum()
        distraction_time = total_time - productive_time
        
        overall_score = productive_time / total_time if total_time > 0 else 0
        
        # Top distractions explicitly
        distraction_df = df[df['is_distracting'] == 1]
        top_distractions = distraction_df.groupby('website')['duration'].sum().sort_values(ascending=False).head(5).to_dict()
        
        # Group by hour
        hourly_dist = df.groupby('hour_of_day')['duration'].sum().to_dict()
        
        return {
            "total_minutes": float(total_time),
            "focus_minutes": float(productive_time),
            "distraction_minutes": float(distraction_time),
            "overall_productivity_score": float(overall_score),
            "top_distractions": top_distractions,
            "hourly_distribution": hourly_dist
        }
    except Exception as e:
        return {"error": str(e)}
