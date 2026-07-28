import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Dynamic database calculation
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "qc_portfolio.db"))

def load_and_clean_data():
    print(f"🔍 Connecting to Database Target: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}.")

    conn = sqlite3.connect(DB_PATH)
    
    # 🌟 Pulling our updated column slots
    query = """
        SELECT 
            m.count_cfu,
            m.limit_cfu,
            t.result_value AS ph_value,
            b.batch_status
        FROM microbial_results m
        JOIN test_results t ON m.batch_id = t.batch_id
        JOIN batches b ON m.batch_id = b.batch_id;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"📊 Raw joined database shape for modeling: {df.shape}")
    
    # Clean outlier/sentinel data integrity test values
    df = df.replace(-999.0, np.nan).dropna()
    print(f"🧹 Shape after clearing null/corrupted sensor features: {df.shape}")
    
    return df

def run_ml_pipeline():
    print("=" * 60)
    print("🔬 INITIALIZING PRODUCTION QC MICROBIAL PREDICTION ENGINE")
    print("=" * 60)
    
    df = load_and_clean_data()
    
    # 🌟 Update feature selection to match our new clean database mappings
    X = df[["count_cfu", "limit_cfu", "ph_value"]]
    y = df["batch_status"].apply(lambda x: 1 if x.upper() == "PASS" else 0)
    
    if len(X) == 0:
        print("❌ Error: No clean training records found after filter rules.")
        return

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("\n🌲 Training Random Forest Classifier model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluations
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n📈 MODEL EVALUATION PERFORMANCE MATRIX:")
    print(f"Overall Accuracy: {acc * 100:.2f}%")
    
    print("\nClassification Report Summary:")
    # Check what classes actually exist in the test split
    unique_classes = sorted(list(set(y_test)))
    
    # Map class integers back to readable labels dynamically
    class_map = {0: "FAIL", 1: "PASS"}
    labels_present = [class_map[c] for c in unique_classes]
    
    print(classification_report(y_test, y_pred, labels=unique_classes, target_names=labels_present))

if __name__ == "__main__":
    run_ml_pipeline()