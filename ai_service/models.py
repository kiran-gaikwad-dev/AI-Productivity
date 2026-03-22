import logging
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
import numpy as np
import pandas as pd
import joblib
import os

# Configure standard logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CLUSTERING_MODEL_PATH = "clustering_model.joblib"
CLASSIFICATION_MODEL_PATH = "classification_model.joblib"
REGRESSION_MODEL_PATH = "regression_model.joblib"
SCALER_PATH = "scaler.joblib"
SCALER_REG_PATH = "scaler_reg.joblib"

clustering_model = None
classification_model = None
regression_model = None
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
        
        # 5. CHAMPION / CHALLENGER Evaluation (A/B Shadowing)
        champion_clf = _load_classification_model()
        is_upgraded = True
        
        if champion_clf is not None:
            # Predict using existing champion on the same physical unseen test set
            champ_pred = champion_clf.predict(X_test)
            champ_f1 = f1_score(y_test, champ_pred, zero_division=0)
            
            if f1 <= champ_f1:
                logging.info(f"Challenger F1 ({f1:.3f}) failed to beat Champion F1 ({champ_f1:.3f}). Retaining Champion model.")
                is_upgraded = False
                f1 = champ_f1 # Return the actual running score
            else:
                logging.info(f"SUCCESS: Challenger F1 ({f1:.3f}) beat Champion F1 ({champ_f1:.3f}). Overwriting Champion.")
        else:
            logging.info("No existing champion found. Challenger automatically deployed.")

        if is_upgraded:
            global classification_model
            classification_model = best_clf
            joblib.dump(best_clf, CLASSIFICATION_MODEL_PATH)
            
        return {
            "status": "Classification model trained + " + ("Deployed" if is_upgraded else "Discarded"),
            "metrics": {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4)
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

def _load_regression_model():
    global regression_model
    regression_model = _load_model(regression_model, REGRESSION_MODEL_PATH)
    return regression_model

def train_regression(df):
    global regression_model
    
    logging.info("Initiating Linear Regression Training Pipeline.")
    REG_FEATURES = [f for f in ML_FEATURES if f != 'duration']
    
    for feature in REG_FEATURES:
        if feature not in df.columns:
            df[feature] = 0
            
    X = df[REG_FEATURES].fillna(0)
    y = df['duration'].fillna(0)
    
    if len(X) < 20:
        logging.warning("Insufficient data for ML Regression validation.")
        return {"status": "Not enough data for Regression"}
        
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # We need a separate scaler for Regression because it uses 7 features, not 8
        scl_reg = StandardScaler()
        X_train_scaled = scl_reg.fit_transform(X_train)
        X_test_scaled = scl_reg.transform(X_test)
        joblib.dump(scl_reg, SCALER_REG_PATH)
        
        reg = LinearRegression()
        reg.fit(X_train_scaled, y_train)
        
        y_pred = reg.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logging.info(f"Regression Optimization Complete. Challenger MSE: {mse:.2f}")
        
        # CHAMPION / CHALLENGER Evaluation
        champion_reg = _load_regression_model()
        is_upgraded = True
        
        if champion_reg is not None:
            champ_pred = champion_reg.predict(X_test_scaled)
            champ_mse = mean_squared_error(y_test, champ_pred)
            
            # Lower MSE is better in Regression
            if mse >= champ_mse:
                logging.info(f"Challenger MSE ({mse:.2f}) failed to beat Champion MSE ({champ_mse:.2f}). Retaining Champion model.")
                is_upgraded = False
                mse = champ_mse
            else:
                logging.info(f"SUCCESS: Challenger MSE ({mse:.2f}) beat Champion MSE ({champ_mse:.2f}). Overwriting Champion.")
        else:
            logging.info("No existing regression champion found. Challenger deployed.")

        if is_upgraded:
            global regression_model
            regression_model = reg
            joblib.dump(reg, REGRESSION_MODEL_PATH)
            
        return {
            "status": "Regression model trained + " + ("Deployed" if is_upgraded else "Discarded"),
            "metrics": {
                "mse": round(mse, 2),
                "r2": round(r2, 4)
            }
        }
    except Exception as e:
        logging.error(f"Regression failure: {str(e)}")
        return {"status": f"Regression error: {str(e)}"}

def _extract_regression_array(features_dict):
    return np.array([[
        features_dict.get('hour_of_day', 12),
        features_dict.get('tab_switch_rate', 0.0),
        features_dict.get('notification_rate', 0.0),
        features_dict.get('is_weekend', 0),
        features_dict.get('device_mobile', 0),
        features_dict.get('device_laptop', 1),
        features_dict.get('device_tablet', 0)
    ]])

def predict_focus_duration(features_dict):
    model = _load_regression_model()
    scl_reg = _load_model(None, SCALER_REG_PATH)
    if not model or not scl_reg:
        return 30.0
        
    try:
        X = _extract_regression_array(features_dict)
        X_scaled = scl_reg.transform(X)
        pred = model.predict(X_scaled)[0]
        # Durations mathematically can't be negative in reality
        return float(max(1.0, pred))
    except Exception:
        return 30.0

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

