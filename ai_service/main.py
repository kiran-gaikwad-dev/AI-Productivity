from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import preprocessing
import models
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

@app.post("/train")
def train_models():
    # Fetch all logs
    raw_data = list(activity_logs.find({}, {"_id": 0}))
    if not raw_data:
        return {"message": "No data available"}
        
    df = preprocessing.preprocess_data(raw_data)
    
    res_cluster = models.train_clustering(df)
    res_class = models.train_classification(df)
    
    return {"clustering": res_cluster, "classification": res_class}

@app.get("/predict/{user_id}")
def user_prediction(user_id: str):
    # Fetch user data
    raw_data = list(activity_logs.find({"user_id": user_id}, {"_id": 0}))
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
    raw_data = list(activity_logs.find({}, {"_id": 0}))
    if not raw_data:
         return {"score": 0}
    df = preprocessing.preprocess_data(raw_data)
    score = models.calculate_productivity_score(df)
    
    # calculate by hour
    hour_dist = df.groupby('hour_of_day')['duration'].sum().to_dict()
    
    # Top distracting sites
    distracting = df[df['is_distracting'] == 1].groupby('website')['duration'].sum().sort_values(ascending=False).head(5).to_dict()
    
    return {
        "overall_productivity_score": score,
        "hourly_distribution": hour_dist,
        "top_distractions": distracting
    }
