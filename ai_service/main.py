from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, ASCENDING, DESCENDING
import os
import time
from dotenv import load_dotenv
import preprocessing
import models
import data_generator

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Use a connection pool maxPoolSize for high concurrency
client = MongoClient(MONGO_URI, maxPoolSize=50)
db = client["ai_productivity"]
activity_logs = db["activity_logs"]
users_col = db["users"]

# Initialize FastAPI exactly once
app = FastAPI(title="AI Productivity Service", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global In-Memory Cache for /stats/global to prevent DB saturation at scale
GLOBAL_STATS_CACHE = {
    "data": None,
    "last_updated": 0
}
CACHE_TTL = 300  # Cache lasts for 5 minutes

@app.on_event("startup")
def startup_db_client():
    """
    Executed once upon server startup.
    Sets up essential DB indexes and pre-loads ML models into memory.
    """
    # 1. Create DB Indexes for scale O(1) lookups
    activity_logs.create_index([("timestamp", DESCENDING)])
    activity_logs.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
    
    # 2. Pre-load ML Models into memory to guarantee ultra-fast first requests
    try:
        models._load_clustering_model()
        models._load_classification_model()
        models._load_regression_model()
        models._load_scaler()
    except Exception as e:
        print(f"Startup Warning: Models not pre-loaded yet (may require initial training). {e}")

def background_training_task():
    """ Runs high CPU ML model training outside the main event loop. """
    raw_data = list(activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10000))
    if raw_data:
        df = preprocessing.preprocess_data(raw_data)
        models.train_clustering(df)
        models.train_classification(df)
        models.train_regression(df)
        
        # Invalidate cache after new data triggers retraining
        GLOBAL_STATS_CACHE["last_updated"] = 0

@app.post("/seed")
def seed_database(background_tasks: BackgroundTasks):
    """
    Production-friendly endpoint to generate logs and train models asynchronously.
    """
    # Generate simulated logs
    batch = data_generator.generate_activity_batch(1000)
    
    # Insert safely into MongoDB
    activity_logs.insert_many(batch)
    
    # Run the window cleanup (Expand to 10k for better ML historical variance)
    data_generator.clean_old_records(keep_limit=10000)
    
    # Queue model training as asynchronous background task
    background_tasks.add_task(background_training_task)
        
    return {
        "status": "success",
        "message": "1000 Synthetic records successfully inserted. Models are training in the background."
    }

@app.post("/train")
def train_models():
    """ Force synchronous training and return metrics (often used by admin tasks) """
    try:
        raw_data = list(activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10000))
        if not raw_data:
            return {"message": "No data available"}
            
        df = preprocessing.preprocess_data(raw_data)
        cluster_res = models.train_clustering(df)
        class_res = models.train_classification(df)
        reg_res = models.train_regression(df)
        
        # Clear cache immediately since models and metrics changed
        GLOBAL_STATS_CACHE["last_updated"] = 0
        
        return {
            "clustering": cluster_res, 
            "classification": class_res,
            "regression": reg_res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/{user_id}")
def user_prediction(user_id: str):
    """ Super-fast indexed prediction lookup for specific user. """
    # Fetch recent user data (Extremely fast due to compound index)
    raw_data = list(activity_logs.find({"user_id": user_id}, {"_id": 0}).sort("timestamp", -1).limit(500))
    if not raw_data:
        raise HTTPException(status_code=404, detail="User not found or no data")
        
    df = preprocessing.preprocess_data(raw_data)
    if df.empty:
         raise HTTPException(status_code=400, detail="User data preprocessing failed")
         
    overall_score = models.calculate_productivity_score(df)
    
    # Predict user cluster based on their average behavior
    avg_features = {
        'hour_of_day': df['hour_of_day'].mean(),
        'duration': df['duration'].mean(),
        'tab_switch_rate': df['tab_switch_rate'].mean(),
        'notification_rate': df['notification_rate'].mean(),
    }
    
    cluster_profile = models.predict_cluster(avg_features)
    
    # Upsert the computed data to the user collection
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
    """ Aggregated scale-ready stats endpoint with 5-minute Time-To-Live caching """
    current_time = time.time()
    
    # 1. High Velocity Cache Hit (O(1))
    if GLOBAL_STATS_CACHE["data"] and (current_time - GLOBAL_STATS_CACHE["last_updated"] < CACHE_TTL):
        return GLOBAL_STATS_CACHE["data"]
        
    try:
        # Cache Miss: Calculate the heavy stats
        raw_data = list(activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10000))
        if not raw_data:
            return {"message": "No data available"}
            
        df = preprocessing.preprocess_data(raw_data)
        if df.empty:
             return {"message": "Preprocessing yield no data"}
        
        total_time = df['duration'].sum()
        productive_time = df[df['is_distracting'] == 0]['duration'].sum()
        distraction_time = total_time - productive_time
        
        overall_score = productive_time / total_time if total_time > 0 else 0
        
        num_days = df['timestamp'].dt.date.nunique()
        num_users = df['user_id'].nunique()
        divisor = num_days * num_users if (num_days * num_users) > 0 else 1
        
        distraction_df = df[df['is_distracting'] == 1]
        top_distractions = (distraction_df.groupby('website')['duration'].sum() / divisor).sort_values(ascending=False).head(5).to_dict()
        
        hourly_dist = []
        for hour in range(24):
            hour_df = df[df['hour_of_day'] == hour]
            f_time = hour_df[hour_df['is_distracting'] == 0]['duration'].sum() / divisor if not hour_df.empty else 0
            d_time = hour_df[hour_df['is_distracting'] == 1]['duration'].sum() / divisor if not hour_df.empty else 0
            hourly_dist.append({
                "hour": f"{hour}:00",
                "focus": round(f_time),
                "distraction": round(d_time)
            })
        
        regression_predictions = []
        for hour in range(24):
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
            
        result = {
            "total_minutes": float(total_time) / divisor,
            "focus_minutes": float(productive_time) / divisor,
            "distraction_minutes": float(distraction_time) / divisor,
            "overall_productivity_score": float(overall_score),
            "top_distractions": top_distractions,
            "hourly_distribution": hourly_dist,
            "regression_predictions": regression_predictions
        }
        
        # Save to Cache memory securely
        GLOBAL_STATS_CACHE["data"] = result
        GLOBAL_STATS_CACHE["last_updated"] = current_time
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
