import duckdb

def build_facts(db_path: str):
    conn = duckdb.connect(db_path)
    try:
        # Fact Expenses: Swap natural keys for Surrogate Keys
        conn.execute("""
            CREATE OR REPLACE TABLE gold.fact_expenses AS 
            SELECT 
                -- Use COALESCE to fallback to the -1 'Unknown' SK if the join fails
                COALESCE(d.date_sk, -1) AS date_sk,
                COALESCE(i.item_sk, -1) AS item_sk,
                COALESCE(b.band_sk, -1) AS band_sk,
                
                -- Keep the actual quantitative facts and degenerate dimensions (notes)
                s.amount,
                s.notes
            FROM silver.cleansed_expenses s
            
            -- 1. Join Date Dimension
            LEFT JOIN gold.dim_date d 
                ON s.txn_date = d.date_actual
                
            -- 2. Join Item Dimension (matching on both to be safe if items share names across categories)
            LEFT JOIN gold.dim_item i 
                ON s.item_name = i.item_name 
               AND s.category_name = i.category
               
            -- 3. Join Spendband Dimension
            LEFT JOIN gold.dim_spendband b 
                ON s.amount BETWEEN b.min_amount AND b.max_amount;
        """)
        print("✓ Gold Layer: fact_expenses built (with SK -1 referential integrity)")
    finally:
        conn.close()