# ParentWise Book Summaries - Project Structure

## Overview

This project contains:
1. **React Web Application** - Live at localhost:3000
2. **MkDocs Static Site** - Ready for deployment at summaries.getparentwise.com
3. **Print-ready HTML files** - For PDF generation

## Project Structure

```
/app/
├── frontend/              # React web application
│   └── src/
│       ├── App.js         # Main application
│       ├── App.css        # Component styles
│       └── index.css      # ParentWise design system
│
├── backend/               # FastAPI backend
│   ├── server.py          # API endpoints
│   └── data/summaries/    # 246 markdown files
│
├── mkdocs-site/           # Static site for Vercel deployment
│   ├── mkdocs.yml         # MkDocs configuration
│   ├── docs/              # Markdown documentation
│   │   ├── index.md       # Homepage
│   │   ├── category-*.md  # Category pages
│   │   ├── all-summaries.md
│   │   └── summaries/     # All 246 summaries
│   ├── site/              # Built static site (deploy this)
│   ├── overrides/         # Custom templates
│   ├── styles/            # Custom CSS
│   ├── generate_docs.py   # Docs structure generator
│   └── generate_pdfs.py   # PDF/HTML generator
│
└── output_html/           # 246 print-ready HTML files
```

## Deployment Options

### Option 1: Deploy MkDocs Static Site to Vercel

The built static site is in `/app/mkdocs-site/site/`

1. Upload the `site/` folder contents to Vercel
2. Configure domain: summaries.getparentwise.com
3. No server required - pure static files

### Option 2: Deploy React App

The React app at localhost:3000 provides a more dynamic experience with:
- Dark/Light theme toggle
- Live search
- Category filtering
- Responsive design

## PDF Generation

Due to environment limitations, PDF files are generated as print-ready HTML:

1. HTML files are in `/app/output_html/`
2. Open any HTML file in a browser
3. Click "Print / Save PDF" button (or Ctrl+P)
4. Select "Save as PDF" as destination

For automated PDF generation, install Pandoc locally:
```bash
# macOS
brew install pandoc

# Windows  
choco install pandoc

# Linux
sudo apt install pandoc
```

Then run:
```bash
pandoc input.md -o output.pdf --pdf-engine=xelatex
```

## Rebuilding the Sites

### Rebuild MkDocs
```bash
cd /app/mkdocs-site
python generate_docs.py  # Regenerate docs structure
mkdocs build             # Build static site
```

### Regenerate Print HTML
```bash
cd /app/mkdocs-site
python generate_pdfs.py
```

## Content Statistics

- **Total Summaries**: 246
- **Categories**: 12
- **Authors**: 222+

### Categories:
| Code | Name | Count |
|------|------|-------|
| COMM | Communication | 14 |
| DIGI | Digital & Technology | 6 |
| FMLY | Family Dynamics | 13 |
| FOUND | Foundational Parenting | 25 |
| GLOB | Global & Cultural | 22 |
| GNDR | Gender-Specific | 13 |
| LIFE | Life Skills | 17 |
| MENT | Mental Health | 19 |
| MISC | Miscellaneous | 64 |
| PRNT | Parent Self-Development | 15 |
| SPEC | Special Needs | 15 |
| TEEN | Teenagers | 23 |

## Design System

The website follows the ParentWise Design Style Guide:
- **Primary Color**: #7c5bff (purple)
- **Dark Mode**: Deep navy backgrounds (#0f1116)
- **Light Mode**: Warm off-white (#faf9f7)
- **Font**: System fonts (SF Pro, Segoe UI, Roboto)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| GET /api/summaries | List all summaries (paginated) |
| GET /api/summaries/:slug | Get single summary |
| GET /api/categories | List all categories with counts |
| GET /api/stats | Get overall statistics |

---

ParentWise • FOCUSED • EMPATHETIC • EXPERT-BACKED
