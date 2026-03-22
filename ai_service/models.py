from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# In a real app, these would be trained and saved using joblib.
# We will create train functionality and hold state in memory for the demo.
clustering_model = None
classification_model = None

def train_clustering(df):
    global clustering_model
    # We cluster users based on 'hour_of_day', 'duration', 'tab_switch_rate', 'notification_rate'
    features = ['hour_of_day', 'duration', 'tab_switch_rate', 'notification_rate']
    X = df[features].fillna(0)
    
    if len(X) < 3:
        return {"status": "Not enough data to train clusters"}
        
    try:
        clustering_model = KMeans(n_clusters=3, random_state=42)
        clustering_model.fit(X)
        return {"status": "Clustering model trained", "clusters": 3}
    except Exception as e:
        return {"status": f"Clustering error: {str(e)}"}

def predict_cluster(features_dict):
    global clustering_model
    if not clustering_model:
        return "Unknown Profile"
        
    X = np.array([[
        features_dict.get('hour_of_day', 12),
        features_dict.get('duration', 30),
        features_dict.get('tab_switch_rate', 0.5),
        features_dict.get('notification_rate', 0.5)
    ]])
    
    cluster_labels = {
        0: "Highly Productive",
        1: "Social Media Heavy",
        2: "Night Procrastinator"
    }
    pred = clustering_model.predict(X)[0]
    return cluster_labels.get(pred, "Unknown Profile")

def train_classification(df):
    global classification_model
    # Predict if a session is productive (1) or distracting (0)
    # Ground truth for training comes from 'is_distracting' inverted
    features = ['hour_of_day', 'duration', 'tab_switch_rate', 'notification_rate']
    X = df[features].fillna(0)
    y = 1 - df['is_distracting'] # 1 is productive, 0 is distracting
    
    if len(X) < 5:
        return {"status": "Not enough data"}
        
    try:
        classification_model = RandomForestClassifier(n_estimators=100, random_state=42)
        classification_model.fit(X, y)
        return {"status": "Classification model trained"}
    except Exception as e:
        return {"status": f"Classification error: {str(e)}"}

def predict_productivity(features_dict):
    global classification_model
    if not classification_model:
        return 0.5
        
    X = np.array([[
        features_dict.get('hour_of_day', 12),
        features_dict.get('duration', 30),
        features_dict.get('tab_switch_rate', 0.5),
        features_dict.get('notification_rate', 0.5)
    ]])
    prob = classification_model.predict_proba(X)[0]
    # prob[1] is probability of productive
    return prob[1] if len(prob) > 1 else 0.5

def calculate_productivity_score(df):
    if df.empty:
        return 0
    total_time = df['duration'].sum()
    if total_time == 0:
        return 0
    distracting_time = df[df['is_distracting'] == 1]['duration'].sum()
    productive_time = total_time - distracting_time
    score = productive_time / total_time
    return score

