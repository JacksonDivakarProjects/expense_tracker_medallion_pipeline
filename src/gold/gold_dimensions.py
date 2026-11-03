import duckdb

def build_dimensions(db_path: str):
    conn = duckdb.connect(db_path)
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS gold;")
        
        # 1. Dim Date (Best Practice YYYYMMDD Smart Key + Contiguous series)
        conn.execute("""
            CREATE OR REPLACE TABLE gold.dim_date AS 
            WITH date_bounds AS (
                SELECT 
                    MIN(txn_date) AS min_date, 
                    MAX(txn_date) AS max_date 
                FROM silver.cleansed_expenses
                WHERE txn_date > '1900-01-01' 
            ),
            continuous_dates AS (
                SELECT UNNEST(generate_series(min_date, max_date, INTERVAL 1 DAY))::DATE AS date_actual
                FROM date_bounds
            )
            -- The explicit Unknown record (19000101)
            SELECT 
                19000101 AS date_sk,
                '1900-01-01'::DATE AS date_actual,
                1900 AS year,
                1 AS month,
                1 AS day,
                'Unknown' AS day_name
            UNION ALL
            -- The actual calendar dates using YYYYMMDD integer keys
            SELECT 
                CAST(strftime(date_actual, '%Y%m%d') AS INTEGER) AS date_sk,
                date_actual,
                EXTRACT(YEAR FROM date_actual) AS year,
                EXTRACT(MONTH FROM date_actual) AS month,
                EXTRACT(DAY FROM date_actual) AS day,
                DAYNAME(date_actual) AS day_name
            FROM continuous_dates
            ORDER BY date_sk;
        """)

        # 2. Dim Item (Item name + Category, Explicit Unknown row)
        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_item_id START 1;
            
            CREATE OR REPLACE TABLE gold.dim_item AS 
            -- The explicit Unknown record (-1)
            SELECT 
                -1 AS item_sk,
                'Unknown Item' AS item_name,
                'Uncategorized' AS category
            UNION ALL
            -- The actual data items with their mapped categories
            SELECT 
                NEXTVAL('seq_item_id') AS item_sk,
                item_name,
                category_name AS category
            FROM (
                SELECT DISTINCT 
                    item_name, 
                    category_name 
                FROM silver.cleansed_expenses 
                WHERE item_name IS NOT NULL 
                  AND item_name != 'Unknown Item'
            );
        """)

        # 3. Dim Spendband (Added Unknown Band)
        conn.execute("""
            CREATE OR REPLACE TABLE gold.dim_spendband (
                band_sk INTEGER,
                band_name VARCHAR,
                min_amount DECIMAL(10,2),
                max_amount DECIMAL(10,2)
            );
            INSERT INTO gold.dim_spendband VALUES 
                (-1, 'Unknown', NULL, NULL),
                (1, 'Gains', -999999.00, 0),
                (2, 'Micro', 0.01, 50.00),
                (3, 'Small', 50.01, 100.00),
                (4, 'Medium', 100.01, 500.00),
                (5, 'Large', 500.01, 9999999.00);
        """)
        print("✓ Gold Layer: Dimensions built (dim_date uses YYYYMMDD smart keys)")
    finally:
        conn.close()