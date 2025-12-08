import os
import glob

# Check all yml, yaml and sql files
files_to_check = glob.glob('**/*.yml', recursive=True) + glob.glob('**/*.yaml', recursive=True)

# Exclude node_modules, venv, target, dbt_packages
exclude_dirs = ['node_modules', 'venv', 'target', 'dbt_packages', '.venv', '.git']
files_to_check = [f for f in files_to_check if not any(exc in f for exc in exclude_dirs)]

bom_files = []
invalid_files = []

for filename in files_to_check:
    try:
        with open(filename, 'rb') as f:
            content = f.read()
        # Check for BOM
        if content.startswith(b'\xef\xbb\xbf'):
            bom_files.append(filename)
        else:
            # Try to decode as UTF-8
            try:
                content.decode('utf-8')
            except UnicodeDecodeError as e:
                invalid_files.append((filename, str(e)[:60]))
    except Exception as e:
        pass

if bom_files:
    print("Files with UTF-8 BOM:")
    for f in bom_files:
        print(f"  {f}")

if invalid_files:
    print("\nInvalid UTF-8 files:")
    for f, err in invalid_files:
        print(f"  {f}: {err}")

if not bom_files and not invalid_files:
    print("All YAML files are clean!")
