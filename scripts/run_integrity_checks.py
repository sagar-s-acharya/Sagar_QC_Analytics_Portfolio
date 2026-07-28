import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "qc_portfolio.db")

print("\n" + "="*60)
print("    RUNNING PROJECT 3: ALCOA+ DATA INTEGRITY COMPLIANCE CHECKS    ")
print("="*60 + "\n")

if not os.path.exists(DB_PATH):
    print("❌ Database file missing! Run 'python initialize_db.py' and 'python import_excel.py' first.")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. ALCOA+: Completeness (Check for NULLs in essential metrics)
cursor.execute("""
    SELECT COUNT(*) 
    FROM test_results 
    WHERE ph_value IS NULL 
       OR moisture_pct IS NULL 
       OR purity_pct IS NULL;
""")
missing_metrics = cursor.fetchone()[0]
print(f"[ALCOA+: Completeness] Missing Critical Metrics: {missing_metrics} issues found.")

# 2. ALCOA+: Timeliness (Check for release dates occurring before batch creation)
cursor.execute("""
    SELECT COUNT(*) 
    FROM batches 
    WHERE qc_release_date < batch_date;
""")
backdated_entries = cursor.fetchone()[0]
print(f"[ALCOA+: Timeliness] Backdated / Pre-dated Entry Errors: {backdated_entries} issues found.")

# 3. ALCOA+: Consistency (Check for batches marked 'Released' despite microbial or PC failures)
cursor.execute("""
    SELECT COUNT(DISTINCT b.batch_id)
    FROM batches b
    LEFT JOIN microbial_results m ON b.batch_id = m.batch_id
    LEFT JOIN test_results t ON b.batch_id = t.batch_id
    WHERE b.batch_status = 'Released'
      AND (m.result_status = 'FAIL' OR t.ph_status = 'FAIL' OR t.moisture_status = 'FAIL' OR t.purity_status = 'FAIL');
""")
status_mismatches = cursor.fetchone()[0]
print(f"[ALCOA+: Consistency] Batch Status Mismatches: {status_mismatches} issues found.")

conn.close()
print("\n" + "="*60 + "\n")