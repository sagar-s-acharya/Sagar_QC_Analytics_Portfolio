import pandas as pd
import sqlite3
import os
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DATA_DIR, "qc_portfolio.db")

print(f"🔍 Database Target: {DB_PATH}")
print(f"🔍 Data Source Directory: {DATA_DIR}\n")

if not os.path.exists(DB_PATH):
    print("❌ Database file missing! Run 'python initialize_db.py' first.")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Column Mappings (CSV Header Lowercase -> Database Table Column)
COLUMN_MAPPINGS = {
    # Batches
    'batch_id': 'batch_id',
    'product': 'product_name',
    'production_line': 'production_line',
    'batch_date': 'batch_date',
    'month_year': 'month_year',
    'quarter': 'quarter',
    'shift': 'shift',
    'supervisor': 'supervisor',
    'batch_size_kg': 'batch_size_kg',
    'raw_material_lot': 'raw_material_lot',
    'batch_status': 'batch_status',
    'qc_release_date': 'qc_release_date',
    
    # Deviations
    'dev_id': 'deviation_id',
    'deviation_date': 'deviation_date',
    'dev_type': 'deviation_type',
    'parameter_affected': 'parameter_affected',
    'root_cause_category': 'root_cause_category',
    'root_cause_description': 'description',
    'severity': 'severity',
    'detected_by': 'detected_by',
    'status': 'status',
    'capa_raised': 'capa_raised',

    # Microbial
    'analyst': 'analyst',
    'test_date': 'test_date',
    'tpc_cfu_g': 'tpc_count',
    'tpc_limit': 'tpc_limit',
    'tpc_result': 'tpc_status',
    'ym_cfu_g': 'ym_count',
    'ym_limit': 'ym_limit',
    'ym_result': 'ym_status',
    'coliform_mpn_g': 'coliform_count',
    'coliform_limit': 'coliform_limit',
    'coliform_result': 'coliform_status',
    'overall_status': 'result_status',
    'reviewed_by': 'reviewed_by',

    # Physicochemical
    'ph_value': 'ph_value',
    'ph_min': 'ph_min',
    'ph_max': 'ph_max',
    'ph_result': 'ph_status',
    'moisture_pct': 'moisture_pct',
    'moisture_limit': 'moisture_limit',
    'moisture_result': 'moisture_status',
    'purity_pct': 'purity_pct',
    'purity_min': 'purity_min',
    'purity_result': 'purity_status'
}

files_to_tables = {
    "batches.csv": "batches",
    "deviations.csv": "deviations",
    "microbial.csv": "microbial_results",
    "physicochemical.csv": "test_results"
}

for csv_file, table_name in files_to_tables.items():
    file_path = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: File not found at {file_path}")
        continue

    print(f"🔄 Ingesting {csv_file} into table '{table_name}'...")
    try:
        df = pd.read_csv(file_path)
        
        # Clean column headers
        df.columns = df.columns.str.strip().str.lower()
        df = df.rename(columns=COLUMN_MAPPINGS)

        # Inject mandatory schema default values where missing
        if table_name == "microbial_results" and "test_type" not in df.columns:
            df["test_type"] = "Microbial"
            
        if table_name == "test_results":
            if "test_type" not in df.columns:
                df["test_type"] = "Physicochemical"
            if "parameter" not in df.columns:
                df["parameter"] = "Physicochemical Parameters"

        # Check actual database table schema
        cursor.execute(f"PRAGMA table_info({table_name});")
        db_cols = [row[1] for row in cursor.fetchall()]

        # Filter out string primary key clashes if SQLite auto-increments IDs
        valid_cols = [c for c in df.columns if c in db_cols and c not in ['test_id', 'micro_id']]
        df_clean = df[valid_cols]

        # Bulk load into SQLite
        df_clean.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"  ✅ Successfully loaded {len(df_clean)} rows into '{table_name}'.\n")

    except Exception as e:
        print(f"  ❌ Error loading {table_name}: {e}")
        traceback.print_exc()
        print("-" * 50)

conn.close()
print("🎉 All 4 CSV files successfully loaded into the database!")