import pandas as pd
import yaml
import os
import xml.etree.ElementTree as ET


def load_profiles(config_path: str) -> dict:
    """
    Load source profiles from a YAML configuration file.
    """
    load_paths = [config_path, "./source_profiles.yaml", "./config/source_profiles.yaml"]
    for path in load_paths:
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            continue
    raise FileNotFoundError(f"No source profile YAML found in paths: {load_paths}")


def detect_source(file_path: str, profiles: dict) -> str:
    """
    Detect the source of a file based on extension and fingerprint columns.
    """
    # Step 1 — Get file extension
    extension = os.path.splitext(file_path)[1].lower()

    # Step 2 — Handle XML (Tally)
    if extension == '.xml':
        return 'tally'

    # Step 3 — Handle TXT (Axis Bank)
    if extension == '.txt':
        return 'axis_bank'

    # Step 4 — Handle Excel
    elif extension in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, nrows=5)
        file_columns = set([c.lower() for c in df.columns])

    # Step 5 — Handle CSV
    elif extension == '.csv':
        df = pd.read_csv(file_path, nrows=5)
        file_columns = set([c.lower() for c in df.columns])

    else:
        raise ValueError(f"Unsupported file type: {extension}")

    # Step 6 — Match against fingerprints
    for source_name, profile in profiles.get('sources', {}).items():
        fingerprints = profile.get('fingerprint_columns', [])
        fingerprints_lower = set(f.lower() for f in fingerprints)

        if fingerprints_lower.issubset(file_columns):
            return source_name

    # Step 7 — No match found
    raise ValueError(f"Unknown source. Columns detected: {file_columns}")


def route_file(file_path: str, config_path: str) -> tuple:
    """
    Load profiles and detect source. Returns (source_name, file_path)
    """
    profiles = load_profiles(config_path)
    source = detect_source(file_path, profiles)
    return source, file_path


if __name__ == "__main__":
    import os

    files = [
        'data/raw/excel_sales.xlsx',
        'data/raw/payment_gateway.csv',
        'data/raw/hdfc_statement.csv',
        'data/raw/tally_export.xml',
        'data/raw/axis_statement_raw.txt'
    ]

    config_path = 'config/source_profiles.yaml'

    # Check if YAML config exists
    if not os.path.exists(config_path):
        print(f"ERROR: YAML config not found at {config_path}")
    else:
        profiles = load_profiles(config_path)

        for f in files:
            print(f"\nProcessing file: {f}")
            if not os.path.exists(f):
                print(f"ERROR: File does not exist!")
                continue
            try:
                source, path = route_file(f, config_path)
                print(f"{os.path.basename(path)} → {source}")
            except Exception as e:
                print(f"ERROR: {e}")
