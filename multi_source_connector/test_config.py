import yaml

with open('config/schema_map.yaml', 'r') as f:
    schema = yaml.safe_load(f)
print("schema_map keys:", list(schema.keys()))

with open('config/source_profiles.yaml', 'r') as f:
    profiles = yaml.safe_load(f)
print("source_profiles keys:", list(profiles.keys()))
print("Sources:", list(profiles['sources'].keys()))
