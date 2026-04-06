import os
import pandas as pd
import sys

# Fix 1 — Correct path so imports work when run from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from parsers.pdf.axis_parser import parse_axis
from parsers.pdf.hdfc_parser import parse_hdfc
from parsers.pdf.exel_parser import parse_exel
from parsers.pdf.payment_parser import parse_payment
from parsers.pdf.tally_parser import parse_tally  # Fix 2 — tally is not in pdf/

CANONICAL_SCHEMA = ["date", "amount", "type", "category", "description", "source", "source_file"]  # Fix 3 — typo CONONICAL

PARSER_MAP = {
    "excel_sales":     parse_exel,
    "payment_gateway": parse_payment,
    "tally":           parse_tally,
    "hdfc_bank":       parse_hdfc,
    "axis_bank":       parse_axis,
}

def enforce_schema(df: pd.DataFrame) -> pd.DataFrame:
    for col in CANONICAL_SCHEMA:
        if col not in df.columns:
            df[col] = None
    return df[CANONICAL_SCHEMA]

def merge_files(file_paths: list, config_path: str) -> pd.DataFrame:
    """
    Input:  list of file paths + config path
    Output: unified DataFrame with canonical schema + row_id
    """
    # Fix 4 — import at top of function, not inside loop
    from detector import route_file

    all_dfs = []
    for file_path in file_paths:
        # Step 1 — Detect source
        source, _ = route_file(file_path, config_path)

        # Step 2 — Get correct parser
        parser = PARSER_MAP.get(source)
        if parser is None:
            print(f"No parser found for source: {source}. Skipping.")
            continue

        # Step 3 — Parse file
        try:  # Fix 5 — wrap in try/except so one bad file doesn't crash everything
            df = parser(file_path)
        except Exception as e:
            print(f"Failed to parse {file_path}: {e}. Skipping.")
            continue

        # Step 4 — Enforce schema
        df = enforce_schema(df)

        print(f"{os.path.basename(file_path)} → {source} → {len(df)} rows")
        all_dfs.append(df)

    # Step 5 — Concatenate all DataFrames
    if not all_dfs:
        raise ValueError("No valid files were parsed. Check data/raw/ has files and detector is working.")

    final_df = pd.concat(all_dfs, ignore_index=True)

    # Step 6 — Add global row_id
    final_df['row_id'] = final_df.index + 1

    return final_df


if __name__ == "__main__":
    import glob

    file_paths = (
        glob.glob('data/raw/*.csv') +
        glob.glob('data/raw/*.xlsx') +
        glob.glob('data/raw/*.xml') +
        glob.glob('data/raw/*.txt')
    )

    if not file_paths:
        print("No files found in data/raw/. Add some data files first.")
    else:
        df = merge_files(file_paths, 'config/source_profiles.yaml')
        print(f"\nFinal Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Sources: {df['source'].unique()}")
        print(f"Row ID range: {df['row_id'].min()} to {df['row_id'].max()}")
        print(df.head(5))