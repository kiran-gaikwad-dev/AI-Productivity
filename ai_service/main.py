from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import preprocessing
import models
import data_generator
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

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
    try:
        raw_data = list(activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10000))
        if not raw_data:
            return {"message": "No data available"}
            
        df = preprocessing.preprocess_data(raw_data)
        cluster_res = models.train_clustering(df)
        class_res = models.train_classification(df)
        reg_res = models.train_regression(df)
        
        return {
            "clustering": cluster_res, 
            "classification": class_res,
            "regression": reg_res
        }
    except Exception as e:
        return {"error": str(e)}

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
        # Fetch ALL recent global logs unconditionally (Prevents 0 0 0 if data isn't perfectly fresh today)
        raw_data = list(activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10000))
        if not raw_data:
            return {"message": "No data available"}
            
        df = preprocessing.preprocess_data(raw_data)
        
        # Calculate aggregate total time correctly
        total_time = df['duration'].sum()
        productive_time = df[df['is_distracting'] == 0]['duration'].sum()
        distraction_time = total_time - productive_time
        
        overall_score = productive_time / total_time if total_time > 0 else 0
        
        # Calculate scaling divisor to get perfectly realistic 24-hour human metrics
        # (Total Hours) / (Unique Days * Unique Users) = Average Minutes per User per Day
        num_days = df['timestamp'].dt.date.nunique()
        num_users = df['user_id'].nunique()
        divisor = num_days * num_users if (num_days * num_users) > 0 else 1
        
        # Top distractions explicitly (Average daily minutes per user)
        distraction_df = df[df['is_distracting'] == 1]
        top_distractions = (distraction_df.groupby('website')['duration'].sum() / divisor).sort_values(ascending=False).head(5).to_dict()
        
        # Segregate Focus vs Distraction by hour (Averaged per user per day)
        hourly_dist = []
        for hour in range(24):
            hour_df = df[df['hour_of_day'] == hour]
            f_time = hour_df[hour_df['is_distracting'] == 0]['duration'].sum() / divisor
            d_time = hour_df[hour_df['is_distracting'] == 1]['duration'].sum() / divisor
            hourly_dist.append({
                "hour": f"{hour}:00",
                "focus": round(f_time),
                "distraction": round(d_time)
            })
        
        # Generate 24-hour Focus predictions based on Linear Regression Model
        regression_predictions = []
        for hour in range(24):
            # Evaluate expected focus time at this specific hour under base zero-distraction conditions
            features = {
                'hour_of_day': hour,
                'tab_switch_rate': 0.0,
                'notification_rate': 0.0,
                'is_weekend': 0,
                'device_laptop': 1,
                'device_mobile': 0,
                'device_tablet': 0
            }
            pred_dur = models.predict_focus_duration(features)
            regression_predictions.append({
                "time": f"{hour}:00",
                "predicted_duration": round(pred_dur)
            })
        
        return {
            "total_minutes": float(total_time) / divisor,
            "focus_minutes": float(productive_time) / divisor,
            "distraction_minutes": float(distraction_time) / divisor,
            "overall_productivity_score": float(overall_score),
            "top_distractions": top_distractions,
            "hourly_distribution": hourly_dist,
            "regression_predictions": regression_predictions
        }
    except Exception as e:
        return {"error": str(e)}
