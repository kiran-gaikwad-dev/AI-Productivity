import pandas as pd
from datetime import datetime

def validate_and_clean(df):
    if df.empty:
        return df
    
    # Validation: Duration must be > 0
    df = df[df['duration'] > 0]
    df = df.dropna(subset=['duration', 'timestamp', 'website'])
    
    # Cleaning: Normalize websites
    df['website'] = df['website'].str.lower().str.strip()
    return df

def feature_engineering(df):
    if df.empty:
        return df
        
    df = df.copy()
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Derived features
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['is_weekend'] = df['timestamp'].dt.weekday >= 5
    
    # Basic distraction indicator based on typical sites
    distracting_sites = ['youtube', 'instagram', 'facebook', 'twitter', 'netflix']
    df['is_distracting'] = df['website'].isin(distracting_sites).astype(int)
    
    # Tab switch rate and notification rate per minute duration
    df['tab_switch_rate'] = df['tab_switches'] / df['duration']
    df['notification_rate'] = df['notifications'] / df['duration']
    
    return df

def preprocess_data(raw_data):
    # raw_data is a list of dicts from MongoDB
    df = pd.DataFrame(raw_data)
    df = validate_and_clean(df)
    df = feature_engineering(df)
    return df
