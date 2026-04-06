import os
import pandas as pd

def parse_exel(file_path: str) -> pd.DataFrame:  # Fix 1 — renamed to match merger import

    # Step 1 — Load Excel file
    df = pd.read_excel(file_path)

    # Step 2 — Rename columns
    df = df.rename(columns={
        'Order Dt':            'date',
        'Total Paid INR':      'amount',
        'Txn Kind':            'type',
        'Random Notes Column': 'category'
    })

    # Step 3 — Normalize type column
    df['type'] = df['type'].replace({
        'Sale':   'income',
        'Refund': 'expense'
    })

    # Step 4 — Add metadata
    df['source']      = 'excel_sales'
    df['source_file'] = os.path.basename(file_path)
    df['description'] = None

    # Step 5 — Return standard schema
    return df[['date', 'amount', 'type', 'category',
               'description', 'source', 'source_file']]


if __name__ == "__main__":
    df = parse_exel('data/raw/excel_sales.xlsx')
    print(f"Shape: {df.shape}")
    print(f"Unique types: {df['type'].unique()}")
    print(df.head(5))