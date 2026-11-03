import sys
from pathlib import Path

# Add the 'src' directory to the system path so we can import our modules
base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir / "src"))

import config
from duckdb_client import load_raw_layer, build_staging_layer

def generate_mock_data():
    print("[Setup] Generating mock CSV files based on sample data...")
    
    # Ensure raw directory exists
    config.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Write dummy Expense Journal
    expenses_content = """Year,Item,Amount (₹),Day,Month,Category,Notes
2026,Repayment,"₹20,000.00",30,7,Repayment,Added
2026,Bus Travel,₹40.00,2,8,Commute,Added
2026,Eggs,₹72.00,3,8,Food And Grocery,Added
2026,Interest From Bond,-₹7.00,4,8,Bonds,Added
"""
    with open(config.EXPENSES_CSV, "w", encoding="utf-8") as f:
        f.write(expenses_content)

    # 2. Write dummy Item & Category Mapping
    mapping_content = """Item name,Category
Repayment,Repayment
Bus Travel,Commute
Eggs & Carrot,Food and Grocery
Interest From Bond,Bonds
"""
    with open(config.MAPPING_CSV, "w", encoding="utf-8") as f:
        f.write(mapping_content)
        
    print(f"✓ Created mock files in {config.RAW_DATA_DIR}\n")

def run_local_test():
    print("=== Starting Local DuckDB Test (Skipping GCP) ===\n")
    
    # Step 0: Create the data
    generate_mock_data()
    
    # Step 2: DuckDB Raw Load
    print("[Step 2] Loading raw data into DuckDB...")
    try:
        load_raw_layer(config.DB_PATH, config.EXPENSES_CSV, config.MAPPING_CSV)
        print("✓ Step 2 Successful\n")
    except Exception as e:
        print(f"✕ Step 2 Failed: {e}")
        sys.exit(1)

    # Step 3: DuckDB Staging Transformation
    print("[Step 3] Building Staging (Silver) Layer...")
    try:
        sample_df = build_staging_layer(config.DB_PATH)
        print("✓ Step 3 Successful")
        print("\n--- Pipeline Complete. Staging Data Preview: ---")
        print(sample_df.to_string(index=False))
        print("------------------------------------------------\n")
    except Exception as e:
        print(f"✕ Step 3 Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_local_test()