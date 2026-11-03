import os
import duckdb
import config

def load_raw_layer(db_path: str, raw_dir: str):
    raw_dir_str = str(raw_dir)
    
    conn = duckdb.connect(db_path)
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        conn.execute("CREATE SCHEMA IF NOT EXISTS silver;")
        conn.execute("CREATE SCHEMA IF NOT EXISTS gold;")
        
        # 1. Ingest Expenses
        wildcard_path = f"{raw_dir_str}/*Expense.csv".replace("\\", "/")
        conn.execute(f"""
            CREATE OR REPLACE TABLE raw.expense_journal AS 
            SELECT * FROM read_csv_auto('{wildcard_path}');
        """)
        
        # 2. Ingest Mapping File
        mapping_path = config.CATEGORY_MAPPING_CSV.replace("\\", "/")
        if os.path.exists(mapping_path):
            conn.execute(f"""
                CREATE OR REPLACE TABLE raw.category_mapping AS 
                SELECT * FROM read_csv_auto('{mapping_path}');
            """)
            print("✓ Bronze Layer built: expense_journal and category_mapping")
        else:
            print("✓ Bronze Layer built: expense_journal (Mapping file missing!)")
            
    finally:
        conn.close()