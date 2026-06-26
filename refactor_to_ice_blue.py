import os
import re

TEMPLATE_DIR = r"c:\Users\atulg\OneDrive\Desktop\DSA Course 90\roadmap\templates\roadmap"

REPLACEMENTS = [
    # --- Backgrounds ---
    (r'\bbg-obsidian\b', 'bg-ice dark:bg-navy-dark'),
    (r'\bbg-\[\#1a0b12\]\b', 'bg-ice dark:bg-navy-dark'),
    (r'\bbg-obsidian-light\/80 backdrop-blur-md\b', 'bg-white/90 backdrop-blur-md dark:bg-navy-light/90'),
    (r'\bbg-obsidian-light\/80\b', 'bg-white/90 dark:bg-navy-light/90'),
    (r'\bbg-obsidian-light\/50\b', 'bg-white/50 dark:bg-navy-light/50'),
    (r'\bbg-obsidian-light\b', 'bg-white dark:bg-navy-light'),
    
    # Accents
    (r'\bbg-rose\b', 'bg-blue dark:bg-blue-dark'),
    (r'\bbg-rose-light\b', 'bg-blue-light dark:bg-blue'),
    (r'\bbg-mauve\b', 'bg-blue-light dark:bg-blue-dark'),
    (r'\bbg-mauve\/20\b', 'bg-blue/10 dark:bg-slate-dark/50'),
    (r'\bbg-mauve\/10\b', 'bg-blue/5 dark:bg-slate-dark/30'),
    (r'\bbg-rose\/20\b', 'bg-blue/20 dark:bg-blue-dark/40'),
    (r'\bbg-rose\/10\b', 'bg-blue/10 dark:bg-blue-dark/20'),
    
    # Hover states
    (r'\bhover:bg-\[\#1a0b12\]\b', 'hover:bg-ice dark:hover:bg-navy-dark'),
    (r'\bhover:bg-rose-light\b', 'hover:bg-blue-light dark:hover:bg-blue'),
    (r'\bhover:bg-rose\b', 'hover:bg-blue dark:hover:bg-blue-dark'),
    (r'\bhover:bg-mauve\/30\b', 'hover:bg-blue/20 dark:hover:bg-slate-dark/60'),

    # --- Text Colors ---
    (r'\btext-ash-dark\b', 'text-slate dark:text-slate-light'),
    (r'\btext-ash\b', 'text-navy dark:text-ice'),
    (r'\btext-mauve\b', 'text-blue dark:text-blue-light'),
    (r'\btext-mauve-light\b', 'text-blue-light dark:text-blue-light'),
    (r'\btext-rose\b', 'text-blue dark:text-blue-light'),
    (r'\btext-rose-light\b', 'text-blue-light dark:text-blue-light'),
    
    # Hover text
    (r'\bhover:text-ash\b', 'hover:text-navy dark:hover:text-ice'),
    (r'\bhover:text-mauve\b', 'hover:text-blue dark:hover:text-blue-light'),
    (r'\bhover:text-mauve-light\b', 'hover:text-blue-light dark:hover:text-blue-light'),
    (r'\bhover:text-rose\b', 'hover:text-blue dark:hover:text-blue-light'),

    # --- Borders ---
    (r'\bborder-mauve\/20\b', 'border-blue/20 dark:border-slate-dark/50'),
    (r'\bborder-mauve\/10\b', 'border-blue/10 dark:border-slate-dark/30'),
    (r'\bborder-rose\b', 'border-blue dark:border-blue-dark'),
    (r'\bborder-rose\/30\b', 'border-blue/30 dark:border-blue-dark/50'),
    
    (r'\bhover:border-rose\b', 'hover:border-blue dark:hover:border-blue-dark'),
    (r'\bhover:border-mauve\/30\b', 'hover:border-blue/30 dark:hover:border-slate-dark/50'),
    
    # --- Rings & Shadows ---
    (r'\bshadow-rose\/30\b', 'shadow-blue/30 dark:shadow-blue-dark/30'),
    (r'\bshadow-rose\/20\b', 'shadow-blue/20 dark:shadow-blue-dark/20'),
    (r'\bshadow-rose\/10\b', 'shadow-blue/10 dark:shadow-blue-dark/10'),
    (r'\bshadow-rose\/5\b', 'shadow-blue/5 dark:shadow-blue-dark/5'),
    (r'\bshadow-mauve\/10\b', 'shadow-blue/10 dark:shadow-blue-dark/10'),
    (r'\bshadow-obsidian\/50\b', 'shadow-navy/5 dark:shadow-navy-dark/50'),
    (r'\bfocus:ring-rose\/50\b', 'focus:ring-blue/50 dark:focus:ring-blue-dark/50'),
    
    # --- Specific gradient replacements ---
    (r'\bfrom-rose\/10\b', 'from-blue/10 dark:from-blue-dark/20'),
    (r'\bfrom-mauve\b', 'from-blue dark:from-blue-light'),
    (r'\bvia-rose\b', 'via-blue-light dark:via-blue'),
    (r'\bto-mauve-light\b', 'to-blue dark:to-blue-light'),
    (r'\bfrom-rose\/0\b', 'from-blue/0 dark:from-blue-dark/0'),
    (r'\bvia-rose\/5\b', 'via-blue/5 dark:via-blue-dark/10'),
    (r'\bto-rose\/0\b', 'to-blue/0 dark:to-blue-dark/0'),
]

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)
        
    # Extra cleanup for lingering colors:
    content = re.sub(r'bg-obsidian/90', 'bg-white/90 dark:bg-navy-dark/90', content)
    content = re.sub(r'bg-obsidian/80', 'bg-white/80 dark:bg-navy-dark/80', content)
    content = re.sub(r'bg-obsidian/60', 'bg-navy-dark/60 dark:bg-navy-dark/80', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {os.path.basename(filepath)}")

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
                
    print(f"Processed {count} HTML files.")

if __name__ == "__main__":
    main()
