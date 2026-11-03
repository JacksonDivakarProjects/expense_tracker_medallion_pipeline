import duckdb

def build_silver_layer(db_path: str):
    conn = duckdb.connect(db_path)
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS silver;")
        
        conn.execute("""
            CREATE OR REPLACE TABLE silver.cleansed_expenses AS 
            SELECT 
                MAKE_DATE(
                    CAST(COALESCE(e.Year, 1900) AS INTEGER), 
                    CAST(COALESCE(e.Month, 1) AS INTEGER), 
                    CAST(COALESCE(e.Day, 1) AS INTEGER)
                ) AS txn_date,
                
                TRIM(COALESCE(e.Item, 'Unknown Item')) AS item_name,
                
                CAST(REPLACE(REPLACE(CAST(COALESCE(e."Amount (₹)", 0) AS VARCHAR), '₹', ''), ',', '') AS DECIMAL(10,2)) AS amount,
                
                -- The Magic: Use the mapped category, fallback to raw category, then 'Uncategorized'
                TRIM(COALESCE(m.standard_category, e.Category, 'Uncategorized')) AS category_name,
                
                TRIM(COALESCE(e.Notes, '')) AS notes
                
            FROM raw.expense_journal e
            LEFT JOIN raw.category_mapping m 
                ON TRIM(e.Category) = m.raw_category
                
            WHERE e."Amount (₹)" IS NOT NULL 
              AND e.Item IS NOT NULL;
        """)
        print("✓ Silver Layer built: cleansed_expenses (categories standardized)")
    finally:
        conn.close()