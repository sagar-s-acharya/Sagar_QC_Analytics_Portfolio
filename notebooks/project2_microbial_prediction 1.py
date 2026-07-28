import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def clean_and_train_pipeline(csv_path):
    print("\n" + "=" * 60)
    print("🔬 INITIALIZING ROBUST PRODUCTION QC MICROBIAL PIPELINE")
    print("=" * 60)
    
    # 1. Load Data Safely
    df = pd.read_csv(csv_path)
    print(f"📦 [EDA]: Raw Dataset Loaded. Shape: {df.shape[0]} rows, {df.shape[1]} features")
    
    # 2. String Cleaning & Target Standardization
    df["Product"] = df["Product"].astype(str).str.strip()
    df["Production_Line"] = df["Production_Line"].astype(str).str.strip()
    df["Overall_Status"] = df["Overall_Status"].astype(str).str.upper().str.strip()
    
    status_clean_map = {
        'PASS': 'PASS', 'PAAS': 'PASS', 'P ASS': 'PASS', 'PASSS': 'PASS',
        'FAIL': 'FAIL', 'FAILL': 'FAIL', 'F-LINE ERROR': 'FAIL'
    }
    df["Overall_Status"] = df["Overall_Status"].map(status_clean_map).fillna('FAIL')
    
    print("\n🎯 [Preprocessing]: Standardized target 'Overall_Status' profile:")
    print(df["Overall_Status"].value_counts())
    
    # 3. Drop High-Cardinality Metadata & Leaky Columns
    metadata_cols = ['Test_ID', 'Batch_ID', 'Test_Date', 'Month_Year', 'Reviewed_By', 'Analyst']
    existing_drops = [col for col in metadata_cols if col in df.columns]
    
    df_model = df.drop(columns=existing_drops)
    print(f"🧹 [Cleaning]: Dropped metadata and target-leakage columns: {existing_drops}")
    
    # 4. Feature and Target Separation
    X = df_model.drop(columns=['Overall_Status'])
    y = df_model['Overall_Status']
    
    # Encode target classes (PASS = 1, FAIL = 0)
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(le, 'models/label_encoder.joblib')
    
    # Future-proof warning-free categorical selection (includes 'string' type)
    categorical_cols = X.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    if categorical_cols:
        X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
        print(f"🛠️ [Preprocessing]: Encoded categorical variables: {categorical_cols}")
    
    # Handle missing values using column medians
    X = X.fillna(X.median())
    
    # 5. Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print(f"📐 [Split Complete]: Train shape: {X_train.shape} | Test shape: {X_test.shape}")
    
    # 6. Model Fitting
    print("🤖 [Training]: Fitting Production Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # 7. Validation Evaluation
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n📊 " + "-"*20 + " EVALUATION REPORT " + "-"*20)
    print(f"🏆 Real-World Model Accuracy: {accuracy:.4f}")
    print("\n📝 Detailed Performance Metrics:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    print("-"*55 + "\n")
    
    # 8. Save production artifacts
    joblib.dump(model, 'models/microbial_rf_model.joblib')
    print("💾 [Deployment]: Model and Encoder serialized to 'models/' directory.")
    
    # 9. Plot Feature Importances
    importances = model.feature_importances_
    indices = np.argsort(importances)[-10:]  # Get top 10 features
    
    plt.figure(figsize=(10, 5))
    plt.barh(range(len(indices)), importances[indices], color='teal', align='center')
    plt.yticks(range(len(indices)), [X.columns[i] for i in indices])
    plt.xlabel('Relative Importance Weight')
    plt.title('Production Process Contamination Drivers (Top 10)')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Robust Path Resolver matching your workspace structure
    possible_paths = [
        "microbial.csv",
        "data/microbial.csv",
        "../data/microbial.csv",
        r"C:\Users\sagar s acharya\OneDrive\Desktop\Sagar_QC_Analytics_Portfolio\microbial.csv"
    ]
    
    resolved_path = None
    for path in possible_paths:
        if os.path.exists(path):
            resolved_path = path
            print(f"🎯 Path Discovery: Found dataset at -> {path}")
            break
            
    if resolved_path:
        clean_and_train_pipeline(resolved_path)
    else:
        print("❌ Error: Could not locate dataset 'microbial.csv'. Check root folder files.")