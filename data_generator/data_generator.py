import time
import random
import datetime
import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["ai_productivity"]
activity_cols = db["activity_logs"]

USERS = [f"U{i}" for i in range(101, 150)]
WEBSITES = ["youtube", "github", "stackoverflow", "instagram", "netflix", "gmail", "docs", "vscode", "twitter", "linkedin"]
DEVICES = ["mobile", "laptop", "tablet"]

def generate_activity_batch(batch_size=1000):
    batch = []
    # Base real-world time constraints
    now = datetime.datetime.now()
    for _ in range(batch_size):
        # Generate varied realistic timestamps (past 7 days)
        random_days_ago = random.randint(0, 7)
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)
        
        simulated_time = now - datetime.timedelta(days=random_days_ago)
        simulated_time = simulated_time.replace(hour=random_hour, minute=random_minute)
        
        # User behavior variation
        user = random.choice(USERS)
        site = random.choice(WEBSITES)
        
        # If site is distracting (e.g. youtube, netflix, instagram at late night) -> higher duration
        is_night = random_hour >= 20 or random_hour <= 4
        is_distracting = site in ['youtube', 'instagram', 'netflix', 'twitter']
        
        duration = random.randint(10, 120) if is_distracting else random.randint(5, 60)
        if is_night and is_distracting:
            duration += random.randint(30, 90) # Night binges
            
        activity = {
            "user_id": user,
            "website": site,
            "duration": duration, # in minutes
            "timestamp": simulated_time.isoformat(),
            "device": random.choice(DEVICES),
            "notifications": random.randint(0, 30) if is_distracting else random.randint(0, 5),
            "tab_switches": random.randint(0, 60) if is_distracting else random.randint(0, 15)
        }
        batch.append(activity)
    
    return batch

def clean_old_records(keep_limit=5000):
    total_docs = activity_cols.count_documents({})
    if total_docs > keep_limit:
        excess = total_docs - keep_limit
        # Find oldest 'excess' documents
        oldest_docs = activity_cols.find().sort("timestamp", 1).limit(excess)
        ids_to_delete = [doc["_id"] for doc in oldest_docs]
        
        # Delete them
        activity_cols.delete_many({"_id": {"$in": ids_to_delete}})
        print(f"Removed {len(ids_to_delete)} old records. Database rolling window maintained.")

def trigger_model_training():
    try:
        response = requests.post("http://localhost:5000/api/ai/train", timeout=20)
        print(f"Model Training Triggered. Response Status: {response.status_code}")
        print(f"Details: {response.json()}")
    except Exception as e:
        print(f"Error triggering training: {e}")

def main():
    print("Starting Advanced Batch Synthetic Data Generator...")
    while True:
        print("\n--- Starting next data generation cycle ---")
        # 1. Generate 1000 records
        batch = generate_activity_batch(1000)
        
        # 2. Insert payload into MongoDB
        activity_cols.insert_many(batch)
        print("Successfully generated and inserted 1000 real-world simulated records.")
        
        # 3. Apply rolling window (remove old records)
        clean_old_records(keep_limit=5000)
        
        # 4. Trigger Model Retraining with fresh batch
        trigger_model_training()
        
        print("Cycle complete. Waiting 60 seconds before next batch...")
        time.sleep(60)

if __name__ == "__main__":
    main()
