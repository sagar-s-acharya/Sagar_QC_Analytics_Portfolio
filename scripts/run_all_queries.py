import sqlite3
import pandas as pd
import os
import re

def run_portfolio_queries():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data", "qc_portfolio.db"))
    
    print("\n📂 CHOOSE THE PORTFOLIO SQL FILE YOU WANT TO RUN:")
    print("1) Analytical Dashboard Queries (project1_queries.sql)")
    print("2) ALCOA+ Data Integrity Compliance (project3_integrity.sql)")
    
    choice = input("Enter selection (1 or 2): ").strip()
    
    if choice == '2':
        sql_filename = 'project3_integrity.sql'
    else:
        sql_filename = 'project1_queries.sql'
        
    sql_path = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "sql", sql_filename))
    
    if not os.path.exists(db_path):
        print(f"❌ Error: Cannot find database file at {db_path}")
        return
        
    if not os.path.exists(sql_path):
        print(f"❌ Error: Cannot find SQL file at {sql_path}")
        return

    conn = sqlite3.connect(db_path)
    
    with open(sql_path, 'r', encoding='utf-8') as file:
        full_sql = file.read()
    
    # Removes comments cleanly including their trailing linebreaks
    clean_sql = re.sub(r'--.*(?:\r?\n|$)', ' ', full_sql)
    queries = [q.strip() for q in clean_sql.split(';') if q.strip()]
    
    print("\n" + "=" * 60)
    print(f"🚀 EXECUTING STATEMENTS FROM: {sql_filename}")
    print("=" * 60)
    
    for idx, query in enumerate(queries, 1):
        print(f"\n📋 [SQL STEP #{idx}]:")
        print(f"Executing: {query[:100].strip()}...")
        print("-" * 55)
        
        try:
            df = pd.read_sql_query(query, conn)
            if df.empty:
                print("(Query executed cleanly - 0 conflict rows discovered)")
            else:
                print(df.to_string(index=False))
        except Exception as e:
            print(f"⚠️ Query Notice: {e}")
            
        print("-" * 55)
        
    conn.close()
    print(f"\n✅ All script rows processed completely inside {sql_filename}!")

if __name__ == '__main__':
    run_portfolio_queries()