import pandas as pd
import pytest
from merger import enforce_schema, merge_files
from analyzer import analyze_transactions
from insights import generate_insights

def test_missing_columns():
    df = pd.DataFrame({"date": ["2026-01-01"], "amount": [1000]})
    df = enforce_schema(df)
    assert all(col in df.columns for col in ["type", "category", "description"])

def test_invalid_amounts():
    df = pd.DataFrame({"date": ["2026-01-01"], "amount": ["abc"], "type": ["credit"], "category": ["Food"]})
    results = analyze_transactions(df)
    assert results["total_inflow"] == 0  # should gracefully handle non-numeric

def test_empty_dataframe():
    df = pd.DataFrame(columns=["date", "amount", "type", "category"])
    results = analyze_transactions(df)
    insights = generate_insights(results)
    assert "No spending categories found." in insights

def test_duplicate_rows():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-01"],
        "amount": [500, 500],
        "type": ["debit", "debit"],
        "category": ["Food", "Food"]
    })
    # Deduplicator should reduce to 1 row
    from deduplicator import deduplicate
    df = deduplicate(df)
    assert len(df) == 1
