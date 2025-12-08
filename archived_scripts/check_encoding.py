import os

files_to_check = ['.user.yml', 'dbt_project.yml', 'packages.yml', 'profiles.yml', 'prefect.yaml']

for filename in files_to_check:
    if os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            # Check for BOM
            if content.startswith(b'\xef\xbb\xbf'):
                print(f"{filename}: HAS UTF-8 BOM")
            else:
                # Try to decode as UTF-8
                try:
                    content.decode('utf-8')
                    print(f"{filename}: Clean UTF-8")
                except UnicodeDecodeError as e:
                    print(f"{filename}: INVALID - {str(e)[:60]}")
        except Exception as e:
            print(f"{filename}: Error reading - {str(e)[:60]}")
