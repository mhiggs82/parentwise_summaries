from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import yaml
import re
from slugify import slugify
import markdown

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

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

# Models
class SummaryBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str
    title: str
    author: str
    category_code: str
    category_name: str
    tags: List[str] = []
    key_principles: List[str] = []
    filename: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SummaryDetail(SummaryBase):
    content: str
    content_html: str

class Category(BaseModel):
    code: str
    name: str
    description: str
    count: int

class SearchResult(BaseModel):
    summaries: List[SummaryBase]
    total: int

# Helper functions
def parse_frontmatter(content: str) -> tuple:
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

def create_slug(filename: str, title: str) -> str:
    """Create a URL-friendly slug from filename or title"""
    # Remove .md extension and create slug
    base = filename.replace('.md', '')
    return slugify(base, max_length=100)

async def load_summaries_to_db():
    """Load all markdown summaries into MongoDB"""
    summaries_dir = ROOT_DIR / 'data' / 'summaries'
    
    if not summaries_dir.exists():
        logging.warning(f"Summaries directory not found: {summaries_dir}")
        return
    
    # Check if already loaded
    count = await db.summaries.count_documents({})
    if count > 0:
        logging.info(f"Summaries already loaded: {count} documents")
        return
    
    logging.info("Loading summaries into database...")
    
    summaries = []
    for filepath in summaries_dir.glob('*.md'):
        if filepath.name == 'qa_summary.txt':
            continue
            
        try:
            content = filepath.read_text(encoding='utf-8')
            metadata, body = parse_frontmatter(content)
            
            # Extract category code from filename (e.g., COMM-001)
            category_match = re.match(r'^([A-Z]+)-\d+', filepath.name)
            category_code = category_match.group(1) if category_match else metadata.get('category_code', 'MISC')
            
            title = metadata.get('title', filepath.stem)
            author = metadata.get('author', 'Unknown Author')
            
            slug = create_slug(filepath.name, title)
            
            # Convert markdown to HTML
            md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
            content_html = md.convert(body)
            
            summary = {
                'id': str(uuid.uuid4()),
                'slug': slug,
                'title': title,
                'author': author,
                'category_code': category_code,
                'category_name': CATEGORY_NAMES.get(category_code, 'Miscellaneous'),
                'tags': metadata.get('tags', []),
                'key_principles': metadata.get('key_principles', []),
                'filename': filepath.name,
                'content': body,
                'content_html': content_html,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            summaries.append(summary)
            
        except Exception as e:
            logging.error(f"Error processing {filepath.name}: {e}")
    
    if summaries:
        await db.summaries.insert_many(summaries)
        logging.info(f"Loaded {len(summaries)} summaries into database")
    
    # Create indexes
    await db.summaries.create_index('slug', unique=True)
    await db.summaries.create_index('category_code')
    await db.summaries.create_index([('title', 'text'), ('author', 'text'), ('tags', 'text')])

# Routes
@api_router.get("/")
async def root():
    return {"message": "ParentWise Book Summaries API"}

@api_router.get("/summaries", response_model=SearchResult)
async def get_summaries(
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all summaries with optional filtering"""
    query = {}
    
    if category:
        query['category_code'] = category.upper()
    
    if search:
        query['$text'] = {'$search': search}
    
    # Get summaries without content for listing
    projection = {'_id': 0, 'content': 0, 'content_html': 0}
    
    cursor = db.summaries.find(query, projection).skip(skip).limit(limit).sort('title', 1)
    summaries = await cursor.to_list(limit)
    
    total = await db.summaries.count_documents(query)
    
    return {"summaries": summaries, "total": total}

@api_router.get("/summaries/{slug}", response_model=SummaryDetail)
async def get_summary(slug: str):
    """Get a single summary by slug"""
    summary = await db.summaries.find_one({'slug': slug}, {'_id': 0})
    
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    return summary

@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    """Get all categories with counts"""
    pipeline = [
        {'$group': {'_id': '$category_code', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]
    
    results = await db.summaries.aggregate(pipeline).to_list(100)
    
    categories = []
    for r in results:
        code = r['_id']
        categories.append({
            'code': code,
            'name': CATEGORY_NAMES.get(code, code),
            'description': CATEGORY_DESCRIPTIONS.get(code, ''),
            'count': r['count']
        })
    
    return categories

@api_router.get("/categories/{code}/summaries", response_model=SearchResult)
async def get_category_summaries(code: str, skip: int = 0, limit: int = 50):
    """Get all summaries in a category"""
    query = {'category_code': code.upper()}
    projection = {'_id': 0, 'content': 0, 'content_html': 0}
    
    cursor = db.summaries.find(query, projection).skip(skip).limit(limit).sort('title', 1)
    summaries = await cursor.to_list(limit)
    
    total = await db.summaries.count_documents(query)
    
    return {"summaries": summaries, "total": total}

@api_router.get("/stats")
async def get_stats():
    """Get overall statistics"""
    total_summaries = await db.summaries.count_documents({})
    
    # Get unique authors
    authors = await db.summaries.distinct('author')
    
    # Get category breakdown
    pipeline = [
        {'$group': {'_id': '$category_code', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    category_counts = await db.summaries.aggregate(pipeline).to_list(100)
    
    return {
        "total_summaries": total_summaries,
        "total_authors": len(authors),
        "total_categories": len(category_counts),
        "categories": {r['_id']: r['count'] for r in category_counts}
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Load summaries on startup"""
    await load_summaries_to_db()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
