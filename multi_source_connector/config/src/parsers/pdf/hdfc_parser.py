import pandas as pd
import os

def parse_hdfc(file_path: str) -> pd.DataFrame:

    # Step 1 — Read CSV
    df = pd.read_csv(file_path)

    # Step 2 — Strip whitespace from column names
    df.columns = [col.strip() for col in df.columns]

    # Step 3 — Rename to canonical names
    df = df.rename(columns={
        'Txn Date':       'date',
        'Narration':      'category',
        'Withdrawal Amt': 'debit',
        'Deposit Amt':    'credit',
    })

    # Step 4 — Drop empty rows
    df = df.dropna(subset=['date'])

    # Step 5 — Clean amounts
    df['debit']  = pd.to_numeric(df['debit'],  errors='coerce').fillna(0)
    df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)

    # Step 6 — Determine amount and type
    def get_amount_and_type(row):
        if row['debit'] > 0:
            return row['debit'], 'expense'
        elif row['credit'] > 0:
            return row['credit'], 'income'
        else:
            return None, None

    df[['amount', 'type']] = df.apply(
        lambda row: pd.Series(get_amount_and_type(row)), axis=1
    )

    # Step 7 — Add metadata
    df['source']      = 'hdfc_bank'
    df['source_file'] = os.path.basename(file_path)
    df['description'] = None

    # Step 8 — Return canonical schema
    return df[['date', 'amount', 'type', 'category',
               'description', 'source', 'source_file']]


if __name__ == "__main__":
    df = parse_hdfc('data/raw/hdfc_statement.csv')
    print(f"Shape: {df.shape}")
    print(f"Unique types: {df['type'].unique()}")
    print(f"Missing amounts: {df['amount'].isna().sum()}")
    print(df.head(5))