# Remove UTF-8 BOM from profiles.yml
with open('profiles.yml', 'rb') as f:
    content = f.read()

# Remove BOM if present
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
    print("Removed UTF-8 BOM from profiles.yml")

# Write back without BOM
with open('profiles.yml', 'wb') as f:
    f.write(content)
    
print("File saved")
