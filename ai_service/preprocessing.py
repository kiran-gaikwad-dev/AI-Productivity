import pandas as pd
from datetime import datetime

def validate_and_clean(df):
    if df.empty:
        return df
    
    # Ensure critical columns exist to prevent crashes (Security/Robustness)
    required_cols = ['duration', 'timestamp', 'website']
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
            
    # Validation: Duration must be > 0 and no nulls in critical areas
    df = df.dropna(subset=required_cols)
    df = df[df['duration'] > 0]
    
    # Cleaning: Normalize websites
    df['website'] = df['website'].astype(str).str.lower().str.strip()
    
    # Handle device default
    if 'device' not in df.columns:
        df['device'] = 'unknown'
        
    if 'tab_switches' not in df.columns:
        df['tab_switches'] = 0
        
    if 'notifications' not in df.columns:
        df['notifications'] = 0
        
    return df

def feature_engineering(df):
    if df.empty:
        return df
        
    df = df.copy()
    
    try:
        # Convert timestamp to datetime (coercing errors to NaT, then dropping)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        
        # Derived Temporal features
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['is_weekend'] = (df['timestamp'].dt.weekday >= 5).astype(int)
        
        # Basic distraction indicator based on typical sites
        distracting_sites = ['youtube', 'instagram', 'facebook', 'twitter', 'netflix']
        df['is_distracting'] = df['website'].isin(distracting_sites).astype(int)
        
        # Behavior Rates (per minute)
        df['tab_switch_rate'] = df['tab_switches'] / df['duration']
        df['notification_rate'] = df['notifications'] / df['duration']
        
        # Fill potentially infinite or NaN values from division by zero
        df.replace([float('inf'), float('-inf')], 0, inplace=True)
        df.fillna(0, inplace=True)
        
        # One-Hot Encode device types securely
        for dev in ['mobile', 'laptop', 'tablet']:
            df[f'device_{dev}'] = (df['device'] == dev).astype(int)
            
    except Exception as e:
        print(f"Error in feature engineering: {e}")
        
    return df

def preprocess_data(raw_data):
    if not raw_data:
        return pd.DataFrame()
    # raw_data is a list of dicts from MongoDB
    df = pd.DataFrame(raw_data)
    df = validate_and_clean(df)
    df = feature_engineering(df)
    return df
