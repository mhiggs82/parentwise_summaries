#!/usr/bin/env python3
"""
Script to generate MkDocs documentation structure from markdown summaries.
This creates category pages and copies all summaries to the docs folder.
"""

import os
import re
import shutil
import yaml
from pathlib import Path
from collections import defaultdict

# Configuration
INPUT_DIR = Path("/app/backend/data/summaries")
OUTPUT_DIR = Path("/app/mkdocs-site/docs")
SUMMARIES_DIR = OUTPUT_DIR / "summaries"

# Category mappings
CATEGORY_NAMES = {
    "COMM": "Communication",
    "DIGI": "Digital & Technology",
    "FMLY": "Family Dynamics",
    "FOUND": "Foundational Parenting",
    "GLOB": "Global & Cultural",
    "GNDR": "Gender-Specific",
    "LIFE": "Life Skills",
    "MENT": "Mental Health",
    "MISC": "Miscellaneous",
    "PRNT": "Parent Self-Development",
    "SPEC": "Special Needs",
    "TEEN": "Teenagers"
}

CATEGORY_DESCRIPTIONS = {
    "COMM": "Books about effective parent-child communication and dialogue techniques",
    "DIGI": "Navigating technology, screen time, and digital wellness for families",
    "FMLY": "Blended families, co-parenting, divorce, and family structures",
    "FOUND": "Core parenting philosophies and foundational approaches",
    "GLOB": "Cultural perspectives, multicultural parenting, and global insights",
    "GNDR": "Gender-specific parenting guidance for raising boys and girls",
    "LIFE": "Building life skills, character, resilience, and purpose in children",
    "MENT": "Mental health, anxiety, emotional intelligence, and psychological well-being",
    "MISC": "Diverse topics including education, work-life balance, and more",
    "PRNT": "Parent self-care, inner healing, and personal development",
    "SPEC": "Special needs, ADHD, autism, and developmental support",
    "TEEN": "Understanding and parenting teenagers and adolescents"
}

def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return {}, content
    
    yaml_str, body = match.groups()
    try:
        metadata = yaml.safe_load(yaml_str) or {}
    except yaml.YAMLError:
        metadata = {}
    
    return metadata, body.strip()

def sanitize_filename(filename):
    """Create a safe filename for MkDocs"""
    # Remove special characters and convert to lowercase
    safe = re.sub(r'[^\w\s\-]', '', filename.replace('.md', ''))
    safe = re.sub(r'\s+', '-', safe).lower()
    return safe[:100] + '.md'

def main():
    # Create output directories
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Collect summaries by category
    summaries_by_category = defaultdict(list)
    all_summaries = []
    
    print(f"Processing summaries from {INPUT_DIR}...")
    
    for filepath in sorted(INPUT_DIR.glob('*.md')):
        if filepath.name == 'qa_summary.txt':
            continue
        
        try:
            content = filepath.read_text(encoding='utf-8')
            metadata, body = parse_frontmatter(content)
            
            # Extract category code from filename
            category_match = re.match(r'^([A-Z]+)-\d+', filepath.name)
            category_code = category_match.group(1) if category_match else metadata.get('category_code', 'MISC')
            
            title = metadata.get('title', filepath.stem)
            author = metadata.get('author', 'Unknown Author')
            
            # Create safe filename
            safe_filename = sanitize_filename(filepath.name)
            
            # Copy to summaries folder
            dest_path = SUMMARIES_DIR / safe_filename
            shutil.copy(filepath, dest_path)
            
            summary_info = {
                'title': title,
                'author': author,
                'category_code': category_code,
                'filename': safe_filename,
                'original_filename': filepath.name,
                'path': f"summaries/{safe_filename}"
            }
            
            summaries_by_category[category_code].append(summary_info)
            all_summaries.append(summary_info)
            
        except Exception as e:
            print(f"Error processing {filepath.name}: {e}")
    
    print(f"Processed {len(all_summaries)} summaries")
    
    # Generate category pages
    print("Generating category pages...")
    for code, name in CATEGORY_NAMES.items():
        summaries = sorted(summaries_by_category.get(code, []), key=lambda x: x['title'])
        description = CATEGORY_DESCRIPTIONS.get(code, '')
        
        content = f"""---
title: {name}
---

# {name}

{description}

**{len(summaries)} book summaries in this category**

"""
        for s in summaries:
            content += f"""
## [{s['title']}]({s['path']})

*by {s['author']}*

---
"""
        
        category_file = OUTPUT_DIR / f"category-{code.lower()}.md"
        category_file.write_text(content, encoding='utf-8')
        print(f"  Created {category_file.name} ({len(summaries)} summaries)")
    
    # Generate all summaries page
    print("Generating all summaries page...")
    all_summaries_sorted = sorted(all_summaries, key=lambda x: x['title'])
    
    content = """---
title: All Book Summaries
---

# All Book Summaries

Browse all {count} book summaries alphabetically.

| Title | Author | Category |
|-------|--------|----------|
""".format(count=len(all_summaries_sorted))
    
    for s in all_summaries_sorted:
        cat_name = CATEGORY_NAMES.get(s['category_code'], s['category_code'])
        content += f"| [{s['title']}]({s['path']}) | {s['author']} | {cat_name} |\n"
    
    all_summaries_file = OUTPUT_DIR / "all-summaries.md"
    all_summaries_file.write_text(content, encoding='utf-8')
    print(f"Created all-summaries.md with {len(all_summaries_sorted)} entries")
    
    print("\nMkDocs documentation structure generated successfully!")
    print(f"  - {len(all_summaries)} summaries copied to {SUMMARIES_DIR}")
    print(f"  - {len(CATEGORY_NAMES)} category pages created")
    print(f"  - All summaries index created")
    print("\nTo build the site, run: cd /app/mkdocs-site && mkdocs build")
    print("The static site will be generated in /app/mkdocs-site/site/")

if __name__ == "__main__":
    main()
