import os
import sqlite3

# Define absolute paths relative to this script file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data", "qc_portfolio.db"))
SCHEMA_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "sql", "schema.sql"))

def init_db():
    print(f"🔍 Initializing database at: {DB_PATH}")
    print(f"🔍 Reading relational schema from: {SCHEMA_PATH}")
    
    # Ensure data folder directory wrapper exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    if not os.path.exists(SCHEMA_PATH):
        print(f"❌ Error: Cannot find schema file at {SCHEMA_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        cursor.executescript(schema_sql)
        conn.commit()
        print("✅ Success! Database folder and empty tables initialized perfectly.")
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()