import pandas as pd

def clean(df, config):
    df = df.copy()

    # -------------------------------------------------
    # STEP 0 — Build normalization lookups
    # -------------------------------------------------
    type_lookup = {}
    for canonical, variants in config["type_normalization"].items():
        for v in variants:
            type_lookup[v.lower().strip()] = canonical

    category_lookup = {}
    for canonical, variants in config["category_normalization"].items():
        for v in variants:
            category_lookup[v.lower().strip()] = canonical

    # -------------------------------------------------
    # STEP 1 — Normalize core fields again (safety)
    # -------------------------------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    df["type"] = (
        df["type"]
        .astype(str).str.lower().str.strip()
        .map(lambda x: type_lookup.get(x, pd.NA))
    )

    df["category"] = (
        df["category"]
        .astype(str).str.lower().str.strip()
        .map(lambda x: category_lookup.get(x, pd.NA))
    )

    # -------------------------------------------------
    # STEP 2 — Enforce amount integrity (post-parser rule)
    # -------------------------------------------------
    df.loc[df["amount"] < 0, "amount"] = pd.NA

    # -------------------------------------------------
    # STEP 3 — Build drop reasons using validator flags
    # -------------------------------------------------
    df["drop_reason"] = pd.NA

    df.loc[df["missing_date"], "drop_reason"] = "missing_date"
    df.loc[df["missing_amount"], "drop_reason"] = "missing_amount"
    df.loc[df["missing_type"], "drop_reason"] = "missing_type"
    df.loc[df["invalid_amount_flag"], "drop_reason"] = "invalid_amount"
    df.loc[df["type"].isna(), "drop_reason"] = "unknown_type"
    df.loc[df["amount"] == 0, "drop_reason"] = "zero_amount"

    # -------------------------------------------------
    # STEP 4 — Create validity flag
    # -------------------------------------------------
    df["is_valid"] = df["drop_reason"].isna()

    # -------------------------------------------------
    # STEP 5 — Cleaning metrics
    # -------------------------------------------------
    total_rows = len(df)
    valid_rows = df["is_valid"].sum()
    dropped_rows = total_rows - valid_rows

    drop_breakdown = (
        df[df["is_valid"] == False]["drop_reason"]
        .value_counts(dropna=False)
        .to_dict()
    )

    cleaning_summary = {
        "total_rows_in": int(total_rows),
        "valid_rows_out": int(valid_rows),
        "dropped_rows": int(dropped_rows),
        "drop_breakdown": drop_breakdown
    }

    # -------------------------------------------------
    # STEP 6 — Keep only valid rows
    # -------------------------------------------------
    df_clean = df[df["is_valid"]].copy()

    return df_clean, cleaning_summary