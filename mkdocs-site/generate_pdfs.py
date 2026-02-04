#!/usr/bin/env python3
"""
PDF Generation Script for ParentWise Book Summaries
Uses WeasyPrint to generate styled PDFs from markdown files.
"""

import os
import re
import yaml
import markdown
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Configuration
INPUT_DIR = Path("/app/backend/data/summaries")
OUTPUT_DIR = Path("/app/output_pdfs")

# ParentWise CSS for PDFs
PDF_CSS = """
@page {
    size: letter;
    margin: 1in;
    @top-center {
        content: "ParentWise Book Summaries";
        font-size: 10pt;
        color: #6b7280;
    }
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        color: #6b7280;
    }
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1d2e;
    max-width: 100%;
}

.header {
    text-align: center;
    margin-bottom: 2em;
    padding-bottom: 1.5em;
    border-bottom: 2px solid #7c5bff;
}

.header h1 {
    color: #7c5bff;
    font-size: 24pt;
    margin-bottom: 0.25em;
    line-height: 1.2;
}

.header .author {
    font-size: 14pt;
    color: #4a5568;
    font-style: italic;
}

.header .category {
    font-size: 10pt;
    color: #7c5bff;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.5em;
}

h1 {
    font-size: 18pt;
    color: #1a1d2e;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

h2 {
    font-size: 14pt;
    color: #7c5bff;
    margin-top: 1.25em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    color: #1a1d2e;
    margin-top: 1em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

h4, h5, h6 {
    font-size: 11pt;
    color: #4a5568;
    margin-top: 0.75em;
    margin-bottom: 0.25em;
}

p {
    margin-bottom: 0.75em;
    text-align: justify;
}

ul, ol {
    margin-bottom: 0.75em;
    padding-left: 1.5em;
}

li {
    margin-bottom: 0.25em;
}

blockquote {
    border-left: 3px solid #7c5bff;
    padding-left: 1em;
    margin: 1em 0;
    color: #4a5568;
    font-style: italic;
}

code {
    background: #f5f3f0;
    padding: 0.1em 0.3em;
    border-radius: 3px;
    font-family: "SF Mono", Monaco, Consolas, monospace;
    font-size: 10pt;
}

pre {
    background: #f5f3f0;
    padding: 1em;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 9pt;
}

pre code {
    background: transparent;
    padding: 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 10pt;
}

th, td {
    border: 1px solid #e8e5e0;
    padding: 0.5em;
    text-align: left;
}

th {
    background: #f5f3f0;
    font-weight: 600;
}

hr {
    border: none;
    border-top: 1px solid #e8e5e0;
    margin: 1.5em 0;
}

strong {
    color: #1a1d2e;
}

a {
    color: #7c5bff;
    text-decoration: none;
}

/* Key principles box */
.principles {
    background: #f8f5ff;
    border: 1px solid #7c5bff;
    border-radius: 8px;
    padding: 1em;
    margin: 1em 0;
}

.principles h4 {
    color: #7c5bff;
    margin-top: 0;
}

.principles ul {
    margin-bottom: 0;
}

/* Tags */
.tags {
    margin: 0.5em 0;
}

.tag {
    display: inline-block;
    background: #f5f3f0;
    color: #4a5568;
    padding: 0.2em 0.5em;
    border-radius: 3px;
    font-size: 9pt;
    margin-right: 0.25em;
}
"""

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

def generate_pdf(filepath, output_dir):
    """Generate a PDF from a markdown file"""
    try:
        content = filepath.read_text(encoding='utf-8')
        metadata, body = parse_frontmatter(content)
        
        # Extract info
        title = metadata.get('title', filepath.stem)
        author = metadata.get('author', 'Unknown Author')
        
        # Get category
        category_match = re.match(r'^([A-Z]+)-\d+', filepath.name)
        category_code = category_match.group(1) if category_match else metadata.get('category_code', 'MISC')
        category_name = CATEGORY_NAMES.get(category_code, category_code)
        
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
        
        # Build full HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
</head>
<body>
    <div class="header">
        <div class="category">{category_name}</div>
        <h1>{title}</h1>
        <div class="author">by {author}</div>
        {tags_html}
    </div>
    {principles_html}
    {body_html}
</body>
</html>
"""
        
        # Generate PDF
        font_config = FontConfiguration()
        css = CSS(string=PDF_CSS, font_config=font_config)
        
        # Create safe filename
        safe_name = re.sub(r'[^\w\s\-]', '', filepath.stem)
        safe_name = re.sub(r'\s+', '-', safe_name)[:80]
        pdf_path = output_dir / f"{safe_name}.pdf"
        
        HTML(string=html_content).write_pdf(pdf_path, stylesheets=[css], font_config=font_config)
        
        return pdf_path
        
    except Exception as e:
        print(f"Error generating PDF for {filepath.name}: {e}")
        return None

def main():
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating PDFs from {INPUT_DIR}...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    success_count = 0
    error_count = 0
    
    md_files = sorted(INPUT_DIR.glob('*.md'))
    total = len([f for f in md_files if f.name != 'qa_summary.txt'])
    
    for i, filepath in enumerate(md_files, 1):
        if filepath.name == 'qa_summary.txt':
            continue
        
        print(f"[{i}/{total}] Processing: {filepath.name[:60]}...", end=" ")
        
        pdf_path = generate_pdf(filepath, OUTPUT_DIR)
        
        if pdf_path:
            print(f"✓ Created")
            success_count += 1
        else:
            print(f"✗ Failed")
            error_count += 1
    
    print()
    print("=" * 60)
    print(f"PDF Generation Complete!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")
    print(f"  Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
