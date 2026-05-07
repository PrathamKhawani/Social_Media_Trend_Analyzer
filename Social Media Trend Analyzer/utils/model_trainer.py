
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import Ridge
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

# Set BASE_DIR to the directory containing Dashboard.py (parent of utils)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_data():
    engagement_path = os.path.join(BASE_DIR, 'engagement.csv')
    hashtags_path = os.path.join(BASE_DIR, 'hashtags.csv')
    ts_path = os.path.join(BASE_DIR, 'time_series.csv')
    
    engagement_df = pd.read_csv(engagement_path)
    try:
        hashtags_df = pd.read_csv(hashtags_path)
    except UnicodeDecodeError:
        hashtags_df = pd.read_csv(hashtags_path, encoding='latin1')
        
    try:
        ts_df = pd.read_csv(ts_path)
    except UnicodeDecodeError:
        ts_df = pd.read_csv(ts_path, encoding='latin1')
        
    return engagement_df, hashtags_df, ts_df

def train_trend_predictor(hashtags_df):
    """Module 1: Trend Predictor (Classification on hashtags.csv)"""
    print("Training Trend Predictor...")
    df = hashtags_df.copy()
    
    categorical_features = ['Platform', 'Content_Type', 'Region']
    for col in categorical_features:
        df[col] = df[col].fillna("Unknown")
        
    target = 'Engagement_Level'
    df[target] = df[target].fillna("Medium")
    
    X = df[categorical_features]
    y = df[target]

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
    ])
    
    model.fit(X, y)
    model_path = os.path.join(BASE_DIR, 'models', 'trend_predictor.pkl')
    joblib.dump(model, model_path)
    print("Trend Predictor saved.")


def train_post_classifier(engagement_df):
    """Module 2: Post Performance Classifier"""
    print("Training Post Performance Classifier...")
    df = engagement_df.copy()
    
    features = ['follower_count', 'media_type', 'content_category', 'post_hour', 'day_of_week', 'hashtags_count', 'caption_length', 'has_call_to_action']
    target = 'performance_bucket_label'
    
    df = df.dropna(subset=[target] + features)
    X = df[features]
    y = df[target]
    
    num_features = ['follower_count', 'post_hour', 'hashtags_count', 'caption_length', 'has_call_to_action']
    cat_features = ['media_type', 'content_category', 'day_of_week']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
        ])
        
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', GradientBoostingClassifier(n_estimators=50, random_state=42))
    ])
    
    model.fit(X, y)
    model_path = os.path.join(BASE_DIR, 'models', 'performance_classifier.pkl')
    joblib.dump(model, model_path)
    print("Post Classifier saved.")


def train_engagement_regressor(engagement_df):
    """Module 3: Engagement Rate Predictor"""
    print("Training Engagement Rate Regressor...")
    df = engagement_df.copy()
    
    features = ['follower_count', 'media_type', 'content_category', 'post_hour', 'day_of_week', 'hashtags_count', 'caption_length', 'has_call_to_action']
    target = 'engagement_rate'
    
    df = df.dropna(subset=[target] + features)
    X = df[features]
    y = df[target]
    
    num_features = ['follower_count', 'post_hour', 'hashtags_count', 'caption_length', 'has_call_to_action']
    cat_features = ['media_type', 'content_category', 'day_of_week']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
        ])
        
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', Ridge(alpha=1.0))
    ])
    
    model.fit(X, y)
    model_path = os.path.join(BASE_DIR, 'models', 'engagement_regressor.pkl')
    joblib.dump(model, model_path)
    print("Engagement Regressor saved.")

def train_hashtag_clustering(hashtags_df):
    """Module 5: Hashtag Clustering"""
    print("Training Hashtag Clustering...")
    df = hashtags_df.copy()
    
    numeric_cols = ['Views', 'Likes', 'Shares', 'Comments']
    df = df.dropna(subset=numeric_cols)
    X = df[numeric_cols]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)
    
    models = {
        'scaler': scaler,
        'kmeans': kmeans,
        'pca': pca
    }
    model_path = os.path.join(BASE_DIR, 'models', 'hashtag_clustering.pkl')
    joblib.dump(models, model_path)
    print("Clustering Model saved.")

def main():
    models_dir = os.path.join(BASE_DIR, 'models')
    os.makedirs(models_dir, exist_ok=True)
    engagement_df, hashtags_df, ts_df = load_data()
    
    train_trend_predictor(hashtags_df)
    train_post_classifier(engagement_df)
    train_engagement_regressor(engagement_df)
    train_hashtag_clustering(hashtags_df)
    print("All Models successfully trained and saved!")

if __name__ == "__main__":
    main()
