import os
import yaml
import pprint
from pathlib import Path

# 1️⃣ Get the folder where this script lives
base_dir = Path(__file__).resolve().parent

# 2️⃣ Paths to check for YAML
possible_paths = [
    base_dir / "source_profiles.yaml",
    base_dir / "config" / "source_profiles.yaml"
]

# 3️⃣ Find the YAML file
yaml_path = next((p for p in possible_paths if p.exists()), None)
if yaml_path is None:
    raise FileNotFoundError("No YAML config file found. Checked:\n" + "\n".join(map(str, possible_paths)))

# 4️⃣ Load YAML safely
with open(yaml_path, "r") as f:
    config_data = yaml.safe_load(f) or {}

print(f"✅ Loaded config from: {yaml_path}")
print(config_data)

# 5️⃣ Ensure outputs folder exists
outputs_folder = base_dir / "outputs"
outputs_folder.mkdir(exist_ok=True)

# 6️⃣ Write a test output file (pretty-printed)
output_file = outputs_folder / "test_output.txt"
with open(output_file, "w") as f:
    f.write("Test run successful.\n\n")
    pprint.pprint(config_data, stream=f)

print(f"✅ Output written to: {output_file}")
