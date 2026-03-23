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
SITES = ['GitHub', 'VS Code', 'Google Docs', 'StackOverflow', 'Figma', 'Slack', 'Jira', 'LinkedIn']
DISTRACTING_APPS = ['Instagram', 'TikTok', 'YouTube', 'Netflix', 'Twitter (X)', 'WhatsApp Chats', 'Snapchat', 'Reddit']
ALL_DEVICES = ['mobile', 'laptop', 'tablet']

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
        user_id = random.choice(USERS) # Changed user to user_id

        # Weight towards mobile apps for typical distraction behaviors
        is_distracting = random.random() < 0.4
        
        if is_distracting:
            site = random.choice(DISTRACTING_APPS)
            # Guarantee mobile device for TikTok, Instagram, Snapchat
            if site in ['TikTok', 'Instagram', 'Snapchat', 'WhatsApp Chats']:
                deviceType = 'mobile'
            else:
                deviceType = random.choices(ALL_DEVICES, weights=[0.6, 0.3, 0.1])[0]
        else:
            site = random.choice(SITES)
            deviceType = random.choices(ALL_DEVICES, weights=[0.1, 0.8, 0.1])[0] # Work is usually laptop
            
        # Give mobile doom-scrolling realistic durations (long periods of short clips)
        if deviceType == 'mobile' and is_distracting:
            duration = random.randint(15, 120) 
            tab_switches = random.randint(30, 150) # High erratic switching on mobile
            notifications = random.randint(5, 40)
        else:
            duration = random.randint(5, 60)
            tab_switches = random.randint(0, 15)
            notifications = random.randint(0, 5)

        activity = {
            "user_id": user_id,
            "website": site,
            "duration": duration,
            "is_distracting": 1 if is_distracting else 0,
            "timestamp": simulated_time.isoformat(),
            "device": deviceType,
            "notifications": notifications,
            "tab_switches": tab_switches
        }
        batch.append(activity)
    
    return batch

def clean_old_records(keep_limit=10000):
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
        # Target the specifically deployed production hosted AI microservice
        response = requests.post("https://ai-productivity-u5fw.onrender.com/train", timeout=60)
        print(f"Model Training Triggered. Response Status: {response.status_code}")
        print(f"Details: {response.json()}")
    except Exception as e:
        print(f"Error triggering training: {e}")

def main():
    print("Starting Advanced Batch Synthetic Data Generator Burst...")
    print("\n--- Starting precise data generation cycle ---")
    
    # 1. Generate 1000 records
    batch = generate_activity_batch(1000)
    
    # 2. Insert payload into MongoDB
    activity_cols.insert_many(batch)
    print("Successfully generated and inserted 1000 real-world simulated records.")
    
    # 3. Apply rolling window (remove old records)
    clean_old_records(keep_limit=5000)
    
    # 4. Trigger Model Retraining with fresh batch
    trigger_model_training()
    
    print("One-shot Data Burst Complete! Your Model is now trained on the absolutely newest metrics.")

if __name__ == "__main__":
    main()
