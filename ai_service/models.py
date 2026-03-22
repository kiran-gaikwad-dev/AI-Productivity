import logging
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import pandas as pd
import joblib
import os

# Configure standard logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CLUSTERING_MODEL_PATH = "clustering_model.joblib"
CLASSIFICATION_MODEL_PATH = "classification_model.joblib"
SCALER_PATH = "scaler.joblib"

clustering_model = None
classification_model = None
scaler = None

# Comprehensive Feature Set
ML_FEATURES = [
    'hour_of_day', 'duration', 'tab_switch_rate', 'notification_rate', 
    'is_weekend', 'device_mobile', 'device_laptop', 'device_tablet'
]

def _load_model(global_var, path):
    if global_var is None and os.path.exists(path):
        return joblib.load(path)
    return global_var

def _load_clustering_model():
    global clustering_model
    clustering_model = _load_model(clustering_model, CLUSTERING_MODEL_PATH)
    return clustering_model

def _load_classification_model():
    global classification_model
    classification_model = _load_model(classification_model, CLASSIFICATION_MODEL_PATH)
    return classification_model

def _load_scaler():
    global scaler
    scaler = _load_model(scaler, SCALER_PATH)
    return scaler

def train_clustering(df):
    global clustering_model
    global scaler
    
    logging.info("Initiating KMeans Clustering Training Pipeline.")
    for feature in ML_FEATURES:
        if feature not in df.columns:
            df[feature] = 0
            
    X = df[ML_FEATURES].fillna(0)
    
    if len(X) < 3:
        logging.warning("Insufficient data for clustering.")
        return {"status": "Not enough data to train clusters"}
        
    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        joblib.dump(scaler, SCALER_PATH)
        
        clustering_model = KMeans(n_clusters=3, random_state=42)
        clustering_model.fit(X_scaled)
        joblib.dump(clustering_model, CLUSTERING_MODEL_PATH)
        logging.info("Successfully trained and persisted KMeans Clustering model.")
        return {"status": "Clustering model trained", "clusters": 3}
    except Exception as e:
        logging.error(f"Clustering error encountered: {str(e)}")
        return {"status": f"Clustering error: {str(e)}"}

def _extract_features_array(features_dict):
    return np.array([[
        features_dict.get('hour_of_day', 12),
        features_dict.get('duration', 30),
        features_dict.get('tab_switch_rate', 0.0),
        features_dict.get('notification_rate', 0.0),
        features_dict.get('is_weekend', 0),
        features_dict.get('device_mobile', 0),
        features_dict.get('device_laptop', 1),
        features_dict.get('device_tablet', 0)
    ]])

def predict_cluster(features_dict):
    model = _load_clustering_model()
    scl = _load_scaler()
    if not model or not scl:
        return "Unknown Profile"
        
    try:
        X = _extract_features_array(features_dict)
        X_scaled = scl.transform(X)
        cluster_labels = { 0: "Highly Productive", 1: "Social Media Heavy", 2: "Night Procrastinator" }
        pred = model.predict(X_scaled)[0]
        return cluster_labels.get(pred, "Unknown Profile")
    except Exception:
        return "Unknown Profile"

def train_classification(df):
    global classification_model
    global scaler
    
    logging.info("Initiating Classification Model Training & Hyperparameter Tuning Pipeline.")
    for feature in ML_FEATURES:
        if feature not in df.columns:
            df[feature] = 0
            
    X = df[ML_FEATURES].fillna(0)
    y = 1 - df['is_distracting'] # 1 is productive, 0 is distracting
    
    if len(X) < 20:
        logging.warning(f"Insufficient data for proper ML classification validation: {len(X)} records found.")
        return {"status": "Not enough data"}
        
    try:
        # Load or fit StandardScaler securely
        if not _load_scaler():
            scl = StandardScaler()
            X_scaled = scl.fit_transform(X)
            scaler = scl
            joblib.dump(scl, SCALER_PATH)
        else:
            X_scaled = scaler.transform(X)
            
        # 1. Standard Dataset Splitting 
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # 2. Hyperparameter Optimization Layer using GridSearchCV
        param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5]
        }
        
        base_clf = RandomForestClassifier(random_state=42)
        grid_search = GridSearchCV(estimator=base_clf, param_grid=param_grid, cv=3, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X_train, y_train)
        
        # Select best optimized model 
        best_clf = grid_search.best_estimator_
        
        # 3. Predict on unseen Test set for unbiased Evaluation
        y_pred = best_clf.predict(X_test)
        
        # 4. Standard Classification Performance Metrics
        acc = accuracy_score(y_test, y_pred)
        # Using zero_division parameter for safety on clean synthetic sets where true positives might be skewed
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        logging.info(f"Model Optimization Complete. Best Params: {grid_search.best_params_}")
        logging.info(f"Test Accuracy: {acc:.3f} | Precision: {prec:.3f} | Recall: {rec:.3f} | F1: {f1:.3f}")
        
        # 5. Persist globally
        classification_model = best_clf
        joblib.dump(best_clf, CLASSIFICATION_MODEL_PATH)
        
        return {
            "status": "Classification model trained",
            "metrics": {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "best_params": grid_search.best_params_
            }
        }
    except Exception as e:
        logging.error(f"Classification failure: {str(e)}")
        return {"status": f"Classification error: {str(e)}"}

def predict_productivity(features_dict):
    model = _load_classification_model()
    scl = _load_scaler()
    if not model or not scl:
        return 0.5
        
    try:
        X = _extract_features_array(features_dict)
        X_scaled = scl.transform(X)
        
        prob = model.predict_proba(X_scaled)[0]
        return prob[1] if len(prob) > 1 else prob[0]
    except Exception:
        return 0.5

def calculate_productivity_score(df):
    if df.empty:
        return 0
    total_time = df.get('duration', pd.Series(dtype=float)).sum()
    if total_time == 0:
        return 0
    
    if 'is_distracting' not in df.columns:
        return 0.5
        
    distracting_time = df[df['is_distracting'] == 1]['duration'].sum()
    productive_time = total_time - distracting_time
    score = productive_time / total_time
    return float(score)

