import sys
import config
from bronze.bronze_extract_gcp import extract_from_drive
from bronze.bronze_ingest_raw import load_raw_layer
from silver.silver_cleanse_scd import build_silver_layer
from gold.gold_dimensions import build_dimensions
from gold.gold_facts import build_facts

def run_pipeline():
    print("=== Starting Modular Data Pipeline ===")
    
    print("[1/5] Landing: Extracting Data from GCP...")
    try:
        extract_from_drive()
    except Exception as e:
        print(f"✕ GCP Extraction Failed: {e}")
        sys.exit(1)
        
    print("\n[2/5] Bronze: Loading Raw Data into DuckDB...")
    load_raw_layer(config.DB_PATH, config.RAW_DATA_DIR)
    
    print("\n[3/5] Silver: Cleansing & Type Casting...")
    build_silver_layer(config.DB_PATH)
    
    print("\n[4/5] Gold: Building Dimensions...")
    build_dimensions(config.DB_PATH)
    
    print("\n[5/5] Gold: Building Facts...")
    build_facts(config.DB_PATH)
    
    print("\n=== Pipeline Complete ===")

if __name__ == "__main__":
    run_pipeline()