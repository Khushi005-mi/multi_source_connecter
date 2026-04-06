import pandas as pd
import os
import glob

def parse_payment(file_path: str) -> pd.DataFrame:
    """
    Parses a payment CSV file and returns a standardized DataFrame.
    - Filters only successful transactions
    - Calculates net amount (Amount INR - Gateway Fee)
    - Adds type, source, source_file, and description columns
    """
    # Step 1 — Load CSV
    df = pd.read_csv(file_path)

    # Step 2 — Detect status column robustly
    status_col = [col for col in df.columns if 'status' in col.lower()]
    if status_col:
        df = df[df[status_col[0]] == 'SUCCESS']
    else:
        print(f"No status column found in {file_path}. Proceeding without filtering.")

    # Step 3 — Rename columns for consistency
    rename_map = {}
    if 'Transaction Date' in df.columns:
        rename_map['Transaction Date'] = 'date'
    if 'Description' in df.columns:
        rename_map['Description'] = 'category'
    df = df.rename(columns=rename_map)

    # Step 4 — Calculate net amount
    amount_col = 'Amount INR' if 'Amount INR' in df.columns else None
    fee_col = 'Gateway Fee' if 'Gateway Fee' in df.columns else None
    if amount_col:
        df['amount'] = df[amount_col].fillna(0)
        if fee_col:
            df['amount'] = df['amount'] - df[fee_col].fillna(0)
    else:
        df['amount'] = 0
        print(f"No Amount INR column found in {file_path}. Setting amount = 0")

    # Step 5 — Create type column
    df['type'] = df['amount'].apply(lambda x: 'income' if x > 0 else 'expense')

    # Step 6 — Add metadata
    df['source'] = 'payment_gateways'
    df['source_file'] = os.path.basename(file_path)
    df['description'] = None  # optional, can be filled if needed

    # Step 7 — Return standardized columns
    columns = ['date', 'amount', 'type', 'category', 'description', 'source', 'source_file']
    for col in columns:
        if col not in df.columns:
            df[col] = None
    return df[columns]

# =========================
# Main execution
# =========================
if __name__ == "__main__":
    # Automatically find the payment CSV anywhere in the project
    csv_files = glob.glob('**/*payment_gateway.csv', recursive=True)
    if not csv_files:
        print("No payment CSV file found in the project.")
    else:
        file_path = csv_files[0]
        print(f"Using payment CSV: {file_path}")
        df = parse_payment(file_path)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Unique types: {df['type'].unique()}")
        print(df.head(5))