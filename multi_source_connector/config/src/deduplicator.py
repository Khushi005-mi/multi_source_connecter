import pandas as pd
from difflib import SequenceMatcher
import re

SOURCE_PRIORITY = {
    'hdfc_bank':       1,
    'axis_bank':       1,
    'payment_gateway': 2,
    'tally':           3,
    'excel_sales':     3,
}

def normalize_description(text: str) -> str:
    """
    Lowercase, remove numbers, remove punctuation,
    remove common noise words
    """
    if not text or pd.isna(text):
        return ''
    text = text.lower()
    text = re.sub(r'\d+', "", text)
    text = re.sub(r'[^\w\s]', "", text)

    # Fix 1 — removed misplaced colon after list, moved inside function
    noise_words = ['upi', 'payment', 'txn', 'ref', 'neft', 'imps']
    for word in noise_words:
        text = text.replace(word, '')
    return text.strip()


def is_duplicate(row1, row2) -> bool:
    """
    Returns True if two rows are duplicates based on:
    - Amount within 1
    - Date within 1 day
    - Description similarity >= 0.85
    """
    # Fix 2 — fixed indentation throughout
    if abs(row1["amount"] - row2["amount"]) > 1:
        return False

    date_diff = abs((pd.to_datetime(row1['date']) - pd.to_datetime(row2['date'])).days)
    if date_diff > 1:
        return False

    desc1 = normalize_description(str(row1["category"]))  # Fix 3 — use category not description
    desc2 = normalize_description(str(row2["category"]))

    # Fix 4 — fixed indentation of similarity line
    similarity = SequenceMatcher(None, desc1, desc2).ratio()
    return similarity >= 0.85


# Fix 5 — corrected function signature (was 'is_duplicate' instead of 'df')
def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input:  merged DataFrame
    Output: deduplicated DataFrame
    """
    # Step 1 — Add priority column
    df['priority'] = df['source'].map(SOURCE_PRIORITY).fillna(99)

    # Step 2 — Normalize descriptions
    df["category"] = df["category"].fillna('').apply(normalize_description)

    # Step 3 — Convert date to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Step 4 — Sort by priority (bank first)
    df = df.sort_values('priority').reset_index(drop=True)  # Fix 6 — was missing sort, and early return

    # Step 5 — Find and remove duplicates
    duplicate_indices = set()

    for i in range(len(df)):
        if i in duplicate_indices:
            continue
        for j in range(i + 1, len(df)):
            if j in duplicate_indices:
                continue
            if is_duplicate(df.iloc[i], df.iloc[j]):
                duplicate_indices.add(j)

    df = df.drop(index=list(duplicate_indices))

    # Step 6 — Drop helper columns
    df = df.drop(columns=['priority'])

    return df  # Fix 7 — return was inside Step 4 block, moved to end


if __name__ == "__main__":
    import glob
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from merger import merge_files

    file_paths = (
        glob.glob('data/raw/*.csv') +
        glob.glob('data/raw/*.xlsx') +
        glob.glob('data/raw/*.xml') +
        glob.glob('data/raw/*.txt')
    )

    df = merge_files(file_paths, 'config/source_profiles.yaml')
    print(f"Before dedup: {len(df)} rows")

    df_clean = deduplicate(df)
    print(f"After dedup: {len(df_clean)} rows")
    print(f"Duplicates removed: {len(df) - len(df_clean)}")
    print(df_clean.head(5))