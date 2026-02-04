# ParentWise Book Summaries - Product Requirements Document

## Original Problem Statement
Convert 256 markdown files (book summaries with YAML frontmatter) into:
- A consistent, public static website hosted at https://summaries.getparentwise.com
- Matching standalone PDF files for each summary
- Use MkDocs for static site generation
- Standardized layout, fonts, colors per ParentWise design style guide
- Dark/Light theme support

## User Personas

### Primary: Parents
- Seeking evidence-based parenting guidance
- Want quick access to book insights without reading entire books
- Value organized, searchable content
- Use mobile and desktop devices

### Secondary: Parenting Professionals
- Therapists, counselors, educators
- Need reference materials
- Want PDF versions for offline use

## Core Requirements (Static)

1. **Content Display**
   - Display 246 book summaries with YAML frontmatter (title, author, tags, key principles)
   - Organize by 12 categories
   - Full markdown rendering

2. **Navigation**
   - Browse by category
   - Search functionality
   - Alphabetical listing

3. **Theme Support**
   - Dark mode (default)
   - Light mode
   - Toggle switch

4. **Outputs**
   - React web application (interactive)
   - MkDocs static site (for Vercel deployment)
   - Print-ready HTML for PDF generation

## What's Been Implemented ✅

### Date: Feb 4, 2026

1. **React Web Application** (localhost:3000)
   - Homepage with hero section, stats, categories, featured summaries
   - Browse page with 246 summaries, category filtering, search
   - Categories page showing all 12 categories
   - Summary detail page with full markdown content
   - Dark/Light theme toggle with localStorage persistence
   - Responsive design for mobile/desktop
   - ParentWise design system integration

2. **FastAPI Backend**
   - `/api/summaries` - list all summaries with filtering
   - `/api/summaries/:slug` - get single summary
   - `/api/categories` - list categories with counts
   - `/api/stats` - overall statistics
   - MongoDB storage with 246 summaries loaded

3. **MkDocs Static Site** (/app/mkdocs-site/site/)
   - Built and ready for deployment
   - 12 category pages
   - All summaries index
   - Material theme with ParentWise styling
   - Search functionality

4. **PDF/HTML Generation** (/app/output_html/)
   - 246 print-ready HTML files generated
   - Each file has "Print / Save PDF" button
   - ParentWise styling applied

## Testing Status
- Backend: 100% (9/9 tests passed)
- Frontend: 100% (10/10 tests passed)

## Prioritized Backlog

### P0 (Critical) - Completed ✅
- [x] Load 246 markdown summaries
- [x] Create browsable web interface
- [x] Dark/Light theme toggle
- [x] Category filtering
- [x] Search functionality
- [x] Build MkDocs static site

### P1 (High Priority)
- [ ] Add PDF download links in React app (requires server-side PDF generation)
- [ ] Deploy MkDocs site to Vercel
- [ ] SEO optimization for MkDocs site

### P2 (Medium Priority)
- [ ] User bookmarking/favorites
- [ ] Reading progress tracking
- [ ] Related summaries suggestions
- [ ] Table of contents for long summaries

### P3 (Future Enhancement)
- [ ] Email newsletter integration
- [ ] User accounts for syncing across devices
- [ ] Audio summaries
- [ ] Highlighted quotes feature

## Technical Stack
- **Frontend**: React 19, Tailwind CSS
- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB
- **Static Site**: MkDocs Material
- **Design**: ParentWise Style Guide

## Deployment Notes
- React app running on localhost:3000
- Backend API on localhost:8001
- MkDocs static site ready in /app/mkdocs-site/site/
- Configure Vercel to serve static files from site/ folder
- Point summaries.getparentwise.com DNS to Vercel

## Next Tasks
1. Deploy MkDocs site to Vercel
2. Configure custom domain
3. Consider adding Pandoc for server-side PDF generation
