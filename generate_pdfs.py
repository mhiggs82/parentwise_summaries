#!/usr/bin/env python3
"""
PDF Generation Script for ParentWise Book Summaries
Uses Pandoc + XeLaTeX to generate styled PDFs from markdown files.
"""

import os
import re
import yaml
import subprocess

# Configuration
input_dir = "/app/Docs"                # folder with .md files
output_dir = "/app/output_pdfs"
os.makedirs(output_dir, exist_ok=True)

# Embedded LaTeX template
latex_template = r"""
\documentclass{article}
\usepackage[margin=1in]{geometry}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{color}
\usepackage{fontspec}
\setmainfont{DejaVu Sans}
\definecolor{headertext}{RGB}{44,62,80}
\definecolor{linkcolor}{RGB}{124,91,255}
\titleformat{\section}{\Large\bfseries\color{headertext}}{}{0em}{}[\titlerule]
\hypersetup{colorlinks=true, linkcolor=linkcolor, urlcolor=linkcolor}
\begin{document}
\title{$title$}
\author{$author$}
\maketitle
$body$
\end{document}
"""

success_count = 0
error_count = 0
total = len([f for f in os.listdir(input_dir) if f.endswith('.md')])

print(f"Generating PDFs from {input_dir}")
print(f"Output directory: {output_dir}")
print(f"Total files to process: {total}")
print("=" * 60)

for i, filename in enumerate(sorted(os.listdir(input_dir)), 1):
    if not filename.endswith('.md'):
        continue
    
    filepath = os.path.join(input_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract YAML frontmatter and body
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        print(f"[{i}/{total}] Skipping {filename[:50]}...: No YAML frontmatter")
        error_count += 1
        continue
    
    yaml_str, body = match.groups()
    try:
        metadata = yaml.safe_load(yaml_str)
    except yaml.YAMLError:
        print(f"[{i}/{total}] Skipping {filename[:50]}...: Invalid YAML")
        error_count += 1
        continue
    
    title = metadata.get('title', 'Untitled').replace('"', '\\"')
    author = metadata.get('author', 'Unknown').replace('"', '\\"')
    
    # Escape LaTeX special characters in title and author
    for char in ['&', '%', '$', '#', '_', '{', '}']:
        title = title.replace(char, '\\' + char)
        author = author.replace(char, '\\' + char)
    
    # Temp files
    md_temp = os.path.join(output_dir, 'temp.md')
    tex_temp = os.path.join(output_dir, 'temp.tex')
    
    with open(md_temp, 'w', encoding='utf-8') as f:
        f.write(body.strip())
    
    with open(tex_temp, 'w', encoding='utf-8') as f:
        f.write(latex_template
                .replace('$title$', title)
                .replace('$author$', author)
                .replace('$body$', body.strip()))
    
    # Output PDF path - create safe filename
    safe_name = re.sub(r'[^\w\s\-]', '', filename.replace('.md', ''))
    safe_name = re.sub(r'\s+', '-', safe_name)[:80]
    pdf_output = os.path.join(output_dir, f"{safe_name}.pdf")
    
    try:
        result = subprocess.run([
            'pandoc', md_temp,
            '-o', pdf_output,
            '--pdf-engine=xelatex',
            '--variable', 'fontsize=12pt',
            '--variable', 'geometry:margin=1in'
        ], check=True, capture_output=True, text=True, timeout=60)
        print(f"[{i}/{total}] ✓ {filename[:50]}...")
        success_count += 1
    except subprocess.CalledProcessError as e:
        print(f"[{i}/{total}] ✗ {filename[:50]}... Error: {e.stderr[:100] if e.stderr else 'Unknown'}")
        error_count += 1
    except subprocess.TimeoutExpired:
        print(f"[{i}/{total}] ✗ {filename[:50]}... Timeout")
        error_count += 1
    
    # Cleanup temp files
    if os.path.exists(md_temp):
        os.remove(md_temp)
    if os.path.exists(tex_temp):
        os.remove(tex_temp)

print("=" * 60)
print(f"PDF generation complete!")
print(f"  Successful: {success_count}")
print(f"  Failed: {error_count}")
print(f"  Output directory: {output_dir}")
