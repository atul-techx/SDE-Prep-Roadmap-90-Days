import os
import re

# Define the root directory to search for HTML files
# Assuming script is run from project root
TEMPLATE_DIR = r"c:\Users\atulg\OneDrive\Desktop\DSA Course 90\roadmap\templates\roadmap"

# Regex patterns and their replacements
# We want to replace standard Tailwind colors (slate, zinc, gray, blue, brand-blue, white, black, etc.)
# with our custom Obsidian Rose palette.
# Note: \b is used for word boundaries to avoid partial matches

REPLACEMENTS = [
    # --- Backgrounds ---
    # Primary Backgrounds
    (r'\b(bg-slate-900|bg-slate-950|dark:bg-\[\#121212\]|bg-\[\#0a0a0a\]|dark:bg-\[\#0a0a0a\]|bg-black)\b', 'bg-obsidian'),
    
    # Secondary Backgrounds (Cards, Panels)
    # Using glassmorphism for lighter backgrounds: bg-obsidian-light/80 backdrop-blur-md
    (r'\b(bg-white|bg-slate-50|bg-slate-100|bg-brand-light|bg-slate-200|bg-slate-800)\b', 'bg-obsidian-light/80 backdrop-blur-md border border-mauve/10'),
    
    # Custom hex replacements for dark backgrounds
    (r'\b(bg-\[\#121212\]|dark:bg-zinc-900|dark:bg-zinc-800)\b', 'bg-obsidian-light'),
    
    # Accents
    (r'\b(bg-brand-blue|bg-indigo-500|bg-indigo-600|bg-blue-500|bg-blue-600)\b', 'bg-rose'),
    (r'\b(bg-indigo-50|bg-blue-50|bg-amber-100|bg-red-50)\b', 'bg-mauve/20'),
    
    # Hover states
    (r'\b(hover:bg-slate-800|hover:bg-slate-700|hover:bg-zinc-700)\b', 'hover:bg-obsidian-lighter'),
    (r'\b(hover:bg-slate-100|hover:bg-slate-200)\b', 'hover:bg-obsidian-lighter/80'),
    (r'\b(hover:bg-brand-blue|hover:brightness-110)\b', 'hover:bg-rose-light'),

    # --- Text Colors ---
    # Primary Text (Light)
    (r'\b(text-slate-800|text-slate-700|text-slate-600|text-slate-900|dark:text-white|text-black)\b', 'text-ash'),
    
    # Secondary Text
    (r'\b(text-slate-500|text-slate-400|text-slate-300|text-zinc-500|text-zinc-400|text-zinc-300|text-white)\b', 'text-ash-dark'),
    
    # Accent Text
    (r'\b(text-brand-blue|text-indigo-500|text-indigo-600|text-blue-500|text-blue-600|text-amber-500|text-amber-600|text-red-600)\b', 'text-mauve'),
    
    # Hover text
    (r'\b(hover:text-white)\b', 'hover:text-ash'),
    (r'\b(hover:text-brand-blue|dark:hover:text-emerald-400)\b', 'hover:text-mauve-light'),

    # --- Borders ---
    (r'\b(border-slate-200|border-slate-300|border-slate-700|border-slate-800|border-zinc-800|border-zinc-700|border-slate-100)\b', 'border-mauve/20'),
    (r'\b(border-brand-blue|border-indigo-100)\b', 'border-rose'),
    
    # --- Rings & Shadows ---
    (r'\b(shadow-brand-blue\/[0-9]+)\b', 'shadow-rose/30'),
    (r'\b(focus:ring-brand-blue|focus:ring-indigo-100)\b', 'focus:ring-rose/50'),
    
    # --- Specific gradient replacements ---
    (r'\b(from-\[\#DFF7FF\]\/20)\b', 'from-rose/10'),
    (r'\b(to-\[\#7FCDFF\]\/20)\b', 'to-mauve/10'),
    (r'\b(from-indigo-50)\b', 'from-rose/20'),
    (r'\b(to-white)\b', 'to-obsidian'),
    (r'\b(bg-indigo-500\/10)\b', 'bg-rose/10'),
    
    # Strip away some excessive dark: prefixes since the whole theme is dark now,
    # but to keep it simple, we just replace the color part.
    (r'dark:bg-obsidian-light\/80', 'bg-obsidian-light/80'),
    (r'dark:bg-obsidian-light', 'bg-obsidian-light'),
    (r'dark:bg-obsidian', 'bg-obsidian'),
    (r'dark:border-mauve\/20', 'border-mauve/20'),
    (r'dark:text-ash-dark', 'text-ash-dark'),
    (r'dark:text-ash', 'text-ash'),
]

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # Apply regex replacements
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)
        
    # Clean up duplicate classes that might arise (like border border-mauve/20 border-mauve/20)
    # A simple regex to remove duplicate adjacent classes (not perfect, but handles common cases)
    # content = re.sub(r'\b(border-mauve/20)\s+\1\b', r'\1', content)

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
