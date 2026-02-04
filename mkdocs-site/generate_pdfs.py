#!/usr/bin/env python3
"""
PDF Generation Script for ParentWise Book Summaries
Uses Pandoc (if available) to generate PDFs from markdown files.

PREREQUISITES:
- Pandoc: https://pandoc.org/installing.html
- XeLaTeX (for custom fonts): Install TeX Live
  - macOS: brew install --cask mactex
  - Windows: https://www.tug.org/texlive/
  - Linux: sudo apt install texlive-xetex texlive-fonts-recommended

If Pandoc is not available, this script generates HTML files that can be
printed to PDF using a browser.
"""

import os
import re
import yaml
import markdown
import subprocess
import shutil
from pathlib import Path

# Configuration
INPUT_DIR = Path("/app/backend/data/summaries")
OUTPUT_DIR = Path("/app/output_pdfs")
HTML_DIR = Path("/app/output_html")

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

# HTML template for print-ready documents
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - ParentWise Summary</title>
    <style>
        @page {{
            size: letter;
            margin: 1in;
        }}
        
        @media print {{
            body {{ font-size: 11pt; }}
            .no-print {{ display: none; }}
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #1a1d2e;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 2px solid #7c5bff;
        }}
        
        .header .category {{
            font-size: 0.75rem;
            color: #7c5bff;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }}
        
        .header h1 {{
            color: #7c5bff;
            font-size: 1.75rem;
            margin: 0.5rem 0;
            line-height: 1.2;
        }}
        
        .header .author {{
            font-size: 1.1rem;
            color: #4a5568;
            font-style: italic;
        }}
        
        .tags {{
            margin-top: 1rem;
        }}
        
        .tag {{
            display: inline-block;
            background: #f5f3f0;
            color: #4a5568;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin: 0.125rem;
        }}
        
        .principles {{
            background: #f8f5ff;
            border: 1px solid #7c5bff;
            border-radius: 8px;
            padding: 1rem;
            margin: 1.5rem 0;
        }}
        
        .principles h4 {{
            color: #7c5bff;
            margin-top: 0;
            margin-bottom: 0.5rem;
        }}
        
        .principles ul {{
            margin: 0;
            padding-left: 1.25rem;
        }}
        
        h1 {{ font-size: 1.5rem; color: #1a1d2e; margin-top: 2rem; border-bottom: 1px solid #e8e5e0; padding-bottom: 0.5rem; }}
        h2 {{ font-size: 1.25rem; color: #7c5bff; margin-top: 1.5rem; }}
        h3 {{ font-size: 1.1rem; color: #1a1d2e; margin-top: 1.25rem; }}
        h4, h5, h6 {{ font-size: 1rem; color: #4a5568; margin-top: 1rem; }}
        
        p {{ margin-bottom: 0.75rem; }}
        
        ul, ol {{ margin-bottom: 0.75rem; padding-left: 1.5rem; }}
        li {{ margin-bottom: 0.25rem; }}
        
        blockquote {{
            border-left: 3px solid #7c5bff;
            padding-left: 1rem;
            margin: 1rem 0;
            color: #4a5568;
            font-style: italic;
        }}
        
        code {{
            background: #f5f3f0;
            padding: 0.1rem 0.3rem;
            border-radius: 3px;
            font-family: "SF Mono", Monaco, Consolas, monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background: #f5f3f0;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 0.85rem;
        }}
        
        pre code {{ background: transparent; padding: 0; }}
        
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }}
        th, td {{ border: 1px solid #e8e5e0; padding: 0.5rem; text-align: left; }}
        th {{ background: #f5f3f0; font-weight: 600; }}
        
        hr {{ border: none; border-top: 1px solid #e8e5e0; margin: 1.5rem 0; }}
        
        .footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #e8e5e0;
            text-align: center;
            color: #6b7280;
            font-size: 0.75rem;
        }}
        
        .print-btn {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: #7c5bff;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }}
        
        .print-btn:hover {{ background: #5d3fd9; }}
    </style>
</head>
<body>
    <button class="print-btn no-print" onclick="window.print()">Print / Save PDF</button>
    
    <div class="header">
        <div class="category">{category}</div>
        <h1>{title}</h1>
        <div class="author">by {author}</div>
        {tags_html}
    </div>
    
    {principles_html}
    
    <div class="content">
        {content}
    </div>
    
    <div class="footer">
        <p>ParentWise Book Summaries • FOCUSED • EMPATHETIC • EXPERT-BACKED</p>
    </div>
</body>
</html>
"""

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

def check_pandoc():
    """Check if Pandoc is available"""
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def generate_html(filepath, output_dir):
    """Generate a print-ready HTML file from a markdown file"""
    try:
        content = filepath.read_text(encoding='utf-8')
        metadata, body = parse_frontmatter(content)
        
        title = metadata.get('title', filepath.stem)
        author = metadata.get('author', 'Unknown Author')
        
        # Get category
        category_match = re.match(r'^([A-Z]+)-\d+', filepath.name)
        category_code = category_match.group(1) if category_match else metadata.get('category_code', 'MISC')
        category = CATEGORY_NAMES.get(category_code, category_code)
        
        key_principles = metadata.get('key_principles', [])
        tags = metadata.get('tags', [])
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
        body_html = md.convert(body)
        
        # Build principles section
        principles_html = ""
        if key_principles:
            principles_html = '<div class="principles"><h4>Key Principles</h4><ul>'
            for p in key_principles:
                principles_html += f'<li>{p}</li>'
            principles_html += '</ul></div>'
        
        # Build tags section
        tags_html = ""
        if tags:
            tags_html = '<div class="tags">'
            for t in tags:
                tags_html += f'<span class="tag">{t}</span>'
            tags_html += '</div>'
        
        # Generate HTML
        html_content = HTML_TEMPLATE.format(
            title=title,
            author=author,
            category=category,
            content=body_html,
            tags_html=tags_html,
            principles_html=principles_html
        )
        
        # Create safe filename
        safe_name = re.sub(r'[^\w\s\-]', '', filepath.stem)
        safe_name = re.sub(r'\s+', '-', safe_name)[:80]
        html_path = output_dir / f"{safe_name}.html"
        
        html_path.write_text(html_content, encoding='utf-8')
        return html_path
        
    except Exception as e:
        print(f"Error generating HTML for {filepath.name}: {e}")
        return None

def main():
    print("=" * 60)
    print("ParentWise PDF/HTML Generation Script")
    print("=" * 60)
    
    # Check for Pandoc
    has_pandoc = check_pandoc()
    
    if has_pandoc:
        print("✓ Pandoc is available - PDF generation possible")
        print("  Run with: pandoc input.md -o output.pdf --pdf-engine=xelatex")
    else:
        print("✗ Pandoc not found - generating print-ready HTML files instead")
        print("  Install Pandoc for direct PDF generation:")
        print("  - macOS: brew install pandoc")
        print("  - Windows: choco install pandoc")
        print("  - Linux: sudo apt install pandoc")
    
    print()
    
    # Create output directory
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {HTML_DIR}")
    print()
    
    success_count = 0
    error_count = 0
    
    md_files = sorted(INPUT_DIR.glob('*.md'))
    total = len([f for f in md_files if f.name != 'qa_summary.txt'])
    
    for i, filepath in enumerate(md_files, 1):
        if filepath.name == 'qa_summary.txt':
            continue
        
        print(f"[{i}/{total}] {filepath.name[:50]}...", end=" ")
        
        html_path = generate_html(filepath, HTML_DIR)
        
        if html_path:
            print("✓")
            success_count += 1
        else:
            print("✗")
            error_count += 1
    
    print()
    print("=" * 60)
    print(f"Generation Complete!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")
    print(f"  Output: {HTML_DIR}")
    print()
    print("To create PDFs:")
    print("  1. Open any HTML file in a web browser")
    print("  2. Click 'Print / Save PDF' button or press Ctrl+P")
    print("  3. Select 'Save as PDF' as the destination")

if __name__ == "__main__":
    main()
