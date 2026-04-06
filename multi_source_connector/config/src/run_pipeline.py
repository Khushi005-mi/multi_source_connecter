import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(__file__))

from merger import merge_files
from cleaner import clean
from analyzer import enforce_schema
from reporter import create_report
from config import load_config
from insights import generate_insights
from analyzer import analyze_transactions
from validator import validate_transactions
from deduplicator import deduplicate

def run_pipeline(raw_data_path: str = "data/raw", config_path: str = "config/source_profiles.yaml"):
    """
    Full pipeline execution:
    1. Merge raw files
    2. Deduplicate
    3. Validate
    4. Clean
    5. Analyze
    6. Generate insights + report
    """

    print("\n=== PIPELINE START ===")

    # Step 1 — Collect raw files
    import glob
    file_paths = {
        glob.glob(os.path.join(raw_data_path, "*.csv")),
        glob.glob(os.path.join(raw_data_path, "*.json")),
        glob.glob(os.path.join(raw_data_path, "*.xlxs")),
        glob.glob(os.path.join(raw_data_path , "*.xls"))
    }
    print(f"Found {sum(len(paths) for paths in file_paths)} raw files.")
    df = merge_files(file_paths, config_path)
    print(f"Merged into Dataframe with {len(df)} rows.")

    # Step 3 — Deduplicate
    df1 = deduplicate(df)
    print(f"duplicate from files found{len(df1)} rows.")
    # Step 4 — Validate
    df2 = validate_transactions(df)
    print(f"validated rows from data{len(df2)}.rows")
    # Step 5 — Clean
    df3 = clean(df)
    print(f"cleaned rows from data{len(df3)}")
    # Step 6 — Analyze
    df4 = analyze_transactions(df)
    print(f"the analyzed data{len(df)}")
    # Step 7 — Insights 
    df5 = generate_insights(results)
    print("insights generated.......")

    # Step 8 — Report
    os.makedirs("reports", exist_ok=True)
    create_report(df, template_path="report.html", output_path="reports/final_report.html")
    print("Report generated at reports/final_report.html")

    print("\n=== PIPELINE END ===")

    if __name__ == "__main__":
     run_pipeline()