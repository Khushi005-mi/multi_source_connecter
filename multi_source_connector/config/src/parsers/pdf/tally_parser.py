import xml.etree.ElementTree as ET
import pandas as pd
import os
def parse_tally(file_path: str) -> pd.DataFrame:
    # Step 1 — Parse XML
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Step 2 — Extract vouchers
    records = []
    for voucher in root.iter('VOUCHER'):
        date = voucher.find('DATE').text
        amount = float(voucher.find("AMOUNT").text)
        voucher_type = voucher.find('VOUCHERTYPENAME').text
        # Fix 1: Correct tag case (NARRATION not NARRaTION)
        # Fix 2: Safe access — some vouchers have no NARRATION tag
        narration_tag = voucher.find("NARRATION")
        narration = narration_tag.text if narration_tag is not None else None
        records.append({
            'date': date,
            'amount': amount,
            'voucher_type': voucher_type,
            'category': narration
        })
    # Step 3 — Create DataFrame
    df = pd.DataFrame(records)
    # Step 4 — Map voucher_type to income/expense
    type_map = {
        'Purchase': 'expense',
        'Receipt': 'income',
        'Sales': 'income',
        'Payment': 'expense'
    }
    df['type'] = df['voucher_type'].map(type_map)
    # Step 5 — Add metadata
    df['source'] = 'tally'
    df['source_file'] = os.path.basename(file_path)
    df['description'] = None
    # Step 6 — Return standard schema
    return df[['date', 'amount', 'type', 'category',
               'description', 'source', 'source_file']]
if __name__ == "__main__":
    df = parse_tally('data/raw/tally_export.xml')
    print(f"Shape: {df.shape}")
    print(f"Unique types: {df['type'].unique()}")
    print(f"Missing category: {df['category'].isna().sum()}")
    print(df.head(5))