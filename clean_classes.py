import os
import re

TEMPLATE_DIR = r"c:\Users\atulg\OneDrive\Desktop\DSA Course 90\roadmap\templates\roadmap"

def clean_classes_in_match(match):
    # match.group(1) contains everything inside class="..."
    classes = match.group(1).split()
    seen = set()
    cleaned = []
    for c in classes:
        # Also clean up weird artifacts like 'border-mauve/10/20'
        if c == 'border-mauve/10/20':
            c = 'border-mauve/20'
        if c == 'bg-obsidian-light/80' and 'bg-obsidian-light' in seen:
            pass # Keep the more specific one if we want, or just deduplicate
            
        if c not in seen:
            seen.add(c)
            cleaned.append(c)
            
    # Resolve conflicts like multiple bgs
    final_classes = []
    has_bg = False
    for c in cleaned:
        if c.startswith('bg-obsidian') or c.startswith('bg-mauve') or c.startswith('bg-rose'):
            if not has_bg:
                final_classes.append(c)
                has_bg = True
        else:
            final_classes.append(c)
            
    return 'class="' + ' '.join(final_classes) + '"'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # Clean up classes
    content = re.sub(r'class="([^"]*)"', clean_classes_in_match, content)
    
    # Clean up duplicate classes not caught (e.g. text-ash-dark text-ash-dark)
    # The clean_classes_in_match should handle this because it's a set.
    
    # Specific fix for border border-mauve/10 border-mauve/20 etc
    def resolve_borders(match):
        classes = match.group(1).split()
        border_colors = [c for c in classes if c.startswith('border-') and c not in ['border-t', 'border-b', 'border-l', 'border-r', 'border-x', 'border-y', 'border-transparent', 'border-dashed', 'border-solid']]
        final_classes = []
        added_border_color = False
        for c in classes:
            if c in border_colors:
                if not added_border_color:
                    final_classes.append(c)
                    added_border_color = True
            else:
                final_classes.append(c)
        return 'class="' + ' '.join(final_classes) + '"'
        
    content = re.sub(r'class="([^"]*)"', resolve_borders, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Cleaned: {os.path.basename(filepath)}")

def main():
    if not os.path.exists(TEMPLATE_DIR):
        print(f"Directory not found: {TEMPLATE_DIR}")
        return

    count = 0
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                process_file(filepath)
                count += 1
                
    print(f"Cleaned {count} HTML files.")

if __name__ == "__main__":
    main()
