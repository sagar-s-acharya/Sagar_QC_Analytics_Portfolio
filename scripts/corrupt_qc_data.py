import pandas as pd
import numpy as np
import os

def create_messy_real_world_data():
    # Targets the file in the data/ directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clean_path = os.path.normpath(os.path.join(script_dir, "..", "data", "microbial.csv"))
    
    if not os.path.exists(clean_path):
        # Fallback to current folder if needed
        clean_path = "microbial.csv"
        
    if not os.path.exists(clean_path):
        print("❌ Error: Could not find your original microbial.csv file!")
        return

    # Load the clean dataset
    df = pd.read_csv(clean_path)
    print(f"📦 Loaded {len(df)} rows of clean data. Starting corruption phase...")
    
    np.random.seed(42) # Keeping it reproducible
    
    # 1. Inject Missing Data (NaNs) - 5% of laboratory metrics vanish
    for col in ["TPC_cfu_g", "YM_cfu_g", "Coliform_MPN_g"]:
        if col in df.columns:
            mask = np.random.rand(len(df)) < 0.05
            df.loc[mask, col] = np.nan
        
    # 2. Inject Structural Typos into Target Labels
    typo_map = {
        'PASS': ['PASS', 'PAAS', 'pass ', 'P ASS', 'PASSS'],
        'FAIL': ['FAIL', 'fail', 'FAILL', 'F-Line Error']
    }
    
    def introduce_typos(status):
        if status in typo_map and np.random.rand() < 0.15: # 15% chance of typo
            return np.random.choice(typo_map[status])
        return status

    if "Overall_Status" in df.columns:
        df["Overall_Status"] = df["Overall_Status"].apply(introduce_typos)
    
    # 3. Inject Outliers & Sensor Failures (-999.0 calibration faults)
    if "TPC_cfu_g" in df.columns:
        mask_fault = np.random.rand(len(df)) < 0.02 # 2% system fault rate
        df.loc[mask_fault, "TPC_cfu_g"] = -999.0
    
    # Extreme outlier spike
    if "Coliform_MPN_g" in df.columns:
        mask_spike = np.random.rand(len(df)) < 0.01
        df.loc[mask_spike, "Coliform_MPN_g"] = 88888.0

    # 4. Inject Malformed Categorical Whitespace
    def add_whitespace(text):
        if isinstance(text, str) and np.random.rand() < 0.10:
            return f"  {text} "
        return text
    if "Product" in df.columns:
        df["Product"] = df["Product"].apply(add_whitespace)

    # 5. Create Duplicate Records (Network submission echo)
    duplicates = df.sample(n=35, random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)

    # Save over the messy file
    df.to_csv(clean_path, index=False)
        
    print("\n" + "🔥" * 20)
    print("⚠️  SUCCESS: YOUR QC DATA IS NOW COMPLETELY MESSY!")
    print("🔥" * 20)
    print(f"New total rows (with duplicates): {len(df)}")
    print("Unique target labels now exist:", df["Overall_Status"].unique() if "Overall_Status" in df.columns else "N/A")

if __name__ == "__main__":
    create_messy_real_world_data()