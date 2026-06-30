import re
import os

filepath = r"C:\Users\atulg\.gemini\antigravity-ide\brain\263b931e-c325-47d9-a0ef-cfc46e58416b\.system_generated\steps\45\content.md"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()
line = lines[41]

# Extract categories and their subcategories
cat_matches = re.finditer(r'\\"category_name\\":\\"(.*?)\\".*?\\"subcategories\\":\[(.*?)\]\}(?=\,|\]\})', line)

# Wait, regex for nested arrays is hard.
# A better way is to split by `\"category_name\":\"`
chunks = line.split(r'\"category_name\":\"')
for chunk in chunks[1:]:
    cat_name = chunk.split(r'\"', 1)[0]
    print(f"Main Topic: {cat_name}")
    
    # Subcategories inside this chunk
    sub_chunks = chunk.split(r'\"subcategory_name\":\"')
    for sub_chunk in sub_chunks[1:]:
        sub_name = sub_chunk.split(r'\"', 1)[0]
        print(f"  Day: {sub_name}")
