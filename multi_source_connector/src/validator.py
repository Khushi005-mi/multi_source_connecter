import pandas as pd

def validate(df):
    df = df.copy()

    if "source_file" not in df.columns:
        df["source_file"] = "unknown_source"

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df["type"] = df["type"].astype(str).str.lower().str.strip()
    df["category"] = df["category"].astype(str).str.strip()

    df["missing_date"] = df["date"].isna()
    df["missing_amount"] = df["amount"].isna()
    df["missing_type"] = df["type"].isin(["nan", "none", ""])
    df["missing_category"] = df["category"].isin(["nan", "none", ""])

    df["invalid_amount_flag"] = (
        df["amount"].isna() | (df["amount"] <= 0)
    )

    total_rows = len(df)

    if total_rows == 0:
        quality_summary = {
            "total_rows": 0,
            "missing_type_pct": 0,
            "missing_amount_pct": 0,
            "missing_category_pct": 0,
            "invalid_amount_count": 0,
            "stop_condition_triggered": True,
            "stop_reason": "Empty dataset"
        }
        return df, quality_summary, pd.DataFrame()

    source_quality = (
        df.groupby("source_file")
          .agg(
              rows=("source_file", "count"),
              missing_type_pct=("missing_type", "mean"),
              missing_amount_pct=("missing_amount", "mean"),
              missing_category_pct=("missing_category", "mean"),
              invalid_amount_pct=("invalid_amount_flag", "mean")
          )
          .reset_index()
    )

    for col in source_quality.columns:
        if col.endswith("_pct"):
            source_quality[col] = source_quality[col].astype(float)

    missing_type_pct = df["missing_type"].mean()
    missing_amount_pct = df["missing_amount"].mean()
    missing_category_pct = df["missing_category"].mean()
    invalid_amount_count = df["invalid_amount_flag"].sum()

    stop_condition_triggered = False
    stop_reason = None

    if missing_type_pct > 0.30:
        stop_condition_triggered = True
        stop_reason = f"Missing type exceeds 30%: {missing_type_pct:.1%}"
    elif missing_amount_pct > 0.10:
        stop_condition_triggered = True
        stop_reason = f"Missing amount exceeds 10%: {missing_amount_pct:.1%}"
    elif (invalid_amount_count / total_rows) > 0.40:
        stop_condition_triggered = True
        stop_reason = "Invalid rows exceed 40%"

    quality_summary = {
        "total_rows": int(total_rows),
        "missing_type_pct": round(float(missing_type_pct), 4),
        "missing_amount_pct": round(float(missing_amount_pct), 4),
        "missing_category_pct": round(float(missing_category_pct), 4),
        "invalid_amount_count": int(invalid_amount_count),
        "stop_condition_triggered": stop_condition_triggered,
        "stop_reason": stop_reason
    }

    return df, quality_summary, source_quality


if __name__ == "__main__":
    print("Validator module loaded successfully")
