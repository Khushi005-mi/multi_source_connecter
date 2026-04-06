import pandas as pd
import os

def parse_axis(file_path: str) -> pd.DataFrame:

    records = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:

        # Skip empty lines
        if line.strip() == "":
            continue

        # Slice by character position
        date        = line[0:10].strip()
        description = line[10:35].strip()
        debit       = line[35:45].strip()
        credit      = line[45:].strip()

        # Skip if no date
        if not date:
            continue

        # Clean amounts
        debit  = debit.replace(',', '')
        credit = credit.replace(',', '')

        # Determine amount and type
        if debit:
            amount   = float(debit)
            txn_type = 'expense'
        elif credit:
            amount   = float(credit)
            txn_type = 'income'
        else:
            amount   = None
            txn_type = None

        records.append({
            'date':   date,
            'amount': amount,
            'type':   txn_type,
            'category': description,
            'description': None,
            'source':      'axis_bank',
            'source_file': os.path.basename(file_path)
        })

    df = pd.DataFrame(records)
    return df[['date', 'amount', 'type', 'category',
               'description', 'source', 'source_file']]


if __name__ == "__main__":
    df = parse_axis('data/raw/axis_statement_raw.txt')
    print(f"Shape: {df.shape}")
    print(f"Unique types: {df['type'].unique()}")
    print(df.head(5))