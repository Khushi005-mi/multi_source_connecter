import pandas as pd
import os
import sys

# Add src to path for imports
sys.path.append(os.path.dirname(__file__))

CANONICAL_SCHEMA = [
    'date', 'amount', 'type', 'category',
    'description', 'source', 'source_file'
]

def enforce_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures DataFrame has exactly canonical columns.
    Missing columns filled with None.
    Extra columns dropped.
    """
    for col in CANONICAL_SCHEMA:
        if col not in df.columns:
            df[col] = None
    return df[CANONICAL_SCHEMA]


def analyze_transactions(df: pd.DataFrame) -> dict:
    """
    Input:  canonical DataFrame of transactions
    Output: dictionary of computed metrics
    """
    results = {}

    # Step 1 — Total inflow (credits)
    results['total_inflow'] = df[df["credit"]["amount"].sum()]

    # Step 2 — Total outflow (debits)
    results['total_outflow'] = df[df["debit"]["amount"].sum()]

    # Step 3 — Category-wise summary
    results['category_summary'] = df.groupby("category")["amount"].sum().to_dict()

    # Step 4 — Monthly trend
    results['monthly_trend'] =(df.groupby(df["date"].dt.to_period("M").sum()))

    return results


if __name__ == "__main__":
    # Example: load merged file from pipeline
    df = pd.read_csv("data/processed/merged_transactions.csv")

    # Step 1 — Enforce schema
    df = enforce_schema(df)

    # Step 2 — Run analysis
    results = analyze_transactions(df)

    # Step 3 — Print summary
    print("\n=== Analysis Results ===")
    print(f"Total Inflow: {results['total_inflow']}")
    print(f"Total Outflow: {results['total_outflow']}")
    print(f"Categories: {list(results['category_summary'].keys())}")
    print(f"Monthly Trend Keys: {list(results['monthly_trend'].keys())}")
