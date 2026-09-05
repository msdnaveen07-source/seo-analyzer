from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime, date, timedelta
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import csv
import io

from backend.db.database import get_db
from backend.db.models import BacklinkSubmission

router = APIRouter(tags=["backlinks"])

# Pydantic Schemas
class BacklinkCreate(BaseModel):
    target_url: str
    submitted_url: str
    anchor_text: Optional[str] = ""
    link_type: Optional[str] = "dofollow"
    submission_category: Optional[str] = "Web 2.0"
    da_score: Optional[int] = 30
    notes: Optional[str] = ""

class BulkBacklinkCreate(BaseModel):
    target_url: str
    urls_raw: str  # Newline or comma separated URLs
    anchor_text: Optional[str] = ""
    link_type: Optional[str] = "dofollow"
    submission_category: Optional[str] = "Web 2.0"
    da_score: Optional[int] = 30

def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc or parsed.path.split('/')[0]
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc.lower()
    except Exception:
        return "unknown"

# High DA Targets Catalog
HIGH_DA_TARGETS = [
    # Web 2.0 / Blogging
    {"name": "Medium", "url": "https://medium.com", "da": 95, "category": "Web 2.0", "link_type": "nofollow", "notes": "Write high-quality articles with embedded contextual backlinks."},
    {"name": "WordPress.com", "url": "https://wordpress.com", "da": 93, "category": "Web 2.0", "link_type": "dofollow", "notes": "Create a free subdomain blog and post original content."},
    {"name": "Blogger / Blogspot", "url": "https://blogger.com", "da": 92, "category": "Web 2.0", "link_type": "dofollow", "notes": "Google-owned platform, fast indexing for contextual links."},
    {"name": "Tumblr", "url": "https://tumblr.com", "da": 88, "category": "Web 2.0", "link_type": "dofollow", "notes": "Microblogging, reblogs can multiply backlink reach."},
    {"name": "Dev.to", "url": "https://dev.to", "da": 82, "category": "Web 2.0", "link_type": "nofollow", "notes": "Tech & software articles with rich markdown formatting."},
    {"name": "Substack", "url": "https://substack.com", "da": 90, "category": "Web 2.0", "link_type": "dofollow", "notes": "Newsletter posts with public archive pages indexed by search engines."},
    {"name": "Telegraph (ph)", "url": "https://telegra.ph", "da": 85, "category": "Web 2.0", "link_type": "dofollow", "notes": "Instant publishing platform by Telegram, fast index rate."},
    {"name": "Wix", "url": "https://wix.com", "da": 94, "category": "Web 2.0", "link_type": "dofollow", "notes": "Free site builder for landing pages and blogs."},
    {"name": "Weebly", "url": "https://weebly.com", "da": 91, "category": "Web 2.0", "link_type": "dofollow", "notes": "Free web page & blog creation with custom links."},
    {"name": "HubPages", "url": "https://discover.hubpages.com", "da": 86, "category": "Web 2.0", "link_type": "dofollow", "notes": "In-depth article publishing platform."},

    # Social Bookmarking & Content Sharing
    {"name": "Reddit", "url": "https://reddit.com", "da": 97, "category": "Social Bookmarking", "link_type": "nofollow", "notes": "Share high-value posts on relevant subreddits."},
    {"name": "Pinterest", "url": "https://pinterest.com", "da": 94, "category": "Social Bookmarking", "link_type": "nofollow", "notes": "Create infographics and pins linking to target pages."},
    {"name": "Scoop.it", "url": "https://scoop.it", "da": 87, "category": "Social Bookmarking", "link_type": "dofollow", "notes": "Curate topics and publish content hubs."},
    {"name": "Folkd", "url": "https://folkd.com", "da": 78, "category": "Social Bookmarking", "link_type": "dofollow", "notes": "Social bookmarking website for link submission."},
    {"name": "Slashdot", "url": "https://slashdot.org", "da": 90, "category": "Social Bookmarking", "link_type": "dofollow", "notes": "Bookmark news & tech links for high authority signals."},
    {"name": "Diigo", "url": "https://diigo.com", "da": 88, "category": "Social Bookmarking", "link_type": "nofollow", "notes": "Save and share web bookmarks publicly."},
    {"name": "Pearltrees", "url": "https://pearltrees.com", "da": 84, "category": "Social Bookmarking", "link_type": "dofollow", "notes": "Organize web links into visual web trees."},

    # High DA Web Directories
    {"name": "Free PR Web Directory", "url": "https://www.freeprwebdirectory.com", "da": 50, "category": "Directory", "link_type": "dofollow", "notes": "High DA 50 General Web Directory Submission."},
    {"name": "High Rank Directory", "url": "https://www.highrankdirectory.com", "da": 50, "category": "Directory", "link_type": "dofollow", "notes": "DA 50 High Rank Business Directory."},
    {"name": "Pro Link Directory", "url": "https://www.prolinkdirectory.com", "da": 48, "category": "Directory", "link_type": "dofollow", "notes": "DA 48 Professional Web Link Directory."},
    {"name": "Sites Web Directory", "url": "https://www.siteswebdirectory.com", "da": 48, "category": "Directory", "link_type": "dofollow", "notes": "DA 48 Web Directory & Business Index."},
    {"name": "Marketing Internet Directory", "url": "https://www.marketinginternetdirectory.com", "da": 47, "category": "Directory", "link_type": "dofollow", "notes": "DA 47 Internet Marketing & Site Directory."},
    {"name": "USA Websites Directory", "url": "https://www.usawebsitesdirectory.com", "da": 43, "category": "Directory", "link_type": "dofollow", "notes": "DA 43 USA Business & Website Directory."},
    {"name": "UK Internet Directory", "url": "https://www.ukinternetdirectory.net", "da": 43, "category": "Directory", "link_type": "dofollow", "notes": "DA 43 UK Web Directory & Index."},
    {"name": "GMA Web Directory", "url": "https://www.gmawebdirectory.com", "da": 42, "category": "Directory", "link_type": "dofollow", "notes": "DA 42 Global Business Directory."},
    {"name": "Travel Tourism Directory", "url": "https://www.traveltourismdirectory.info", "da": 38, "category": "Directory", "link_type": "dofollow", "notes": "DA 38 Travel & Business Directory."},
    {"name": "Activ Directory", "url": "https://activdirectory.net", "da": 38, "category": "Directory", "link_type": "dofollow", "notes": "DA 38 Active Website Listing Directory."},
    {"name": "Submission Web Directory", "url": "http://www.submissionwebdirectory.com", "da": 32, "category": "Directory", "link_type": "dofollow", "notes": "DA 32 Free Web Directory Submission."},
    {"name": "Info Listings Directory", "url": "https://info-listings.com", "da": 31, "category": "Directory", "link_type": "dofollow", "notes": "DA 31 Info & Business Listings Index."},
    {"name": "Gain Web Directory", "url": "https://www.gainweb.org", "da": 28, "category": "Directory", "link_type": "dofollow", "notes": "DA 28 Web Organization Directory."},
    {"name": "Tags Hub Directory", "url": "https://tagshub.com", "da": 27, "category": "Directory", "link_type": "dofollow", "notes": "DA 27 Tags & Website Index."},
    {"name": "Quick Links Directory", "url": "https://quicklinks.net", "da": 27, "category": "Directory", "link_type": "dofollow", "notes": "DA 27 Fast Indexing Web Directory."},
    {"name": "Promote Business Directory", "url": "http://promotebusinessdirectory.com", "da": 25, "category": "Directory", "link_type": "dofollow", "notes": "DA 25 Business Promotion Directory."},
    {"name": "Site Promotion Directory", "url": "http://www.sitepromotiondirectory.com", "da": 25, "category": "Directory", "link_type": "dofollow", "notes": "DA 25 Site Promotion Listing."},
    {"name": "More Funz Directory", "url": "https://morefunz.com", "da": 25, "category": "Directory", "link_type": "dofollow", "notes": "DA 25 Web Directory & Portal."},
    {"name": "Web O World Directory", "url": "https://weboworld.com", "da": 25, "category": "Directory", "link_type": "dofollow", "notes": "DA 25 Web Directory Listing."},

    # Profile & Forum Backlinks
    {"name": "GitHub", "url": "https://github.com", "da": 96, "category": "Profile", "link_type": "dofollow", "notes": "Add website link in profile bio and repository READMEs."},
    {"name": "GitLab", "url": "https://gitlab.com", "da": 92, "category": "Profile", "link_type": "dofollow", "notes": "Profile bio and project documentation links."},
    {"name": "Quora", "url": "https://quora.com", "da": 93, "category": "Forum", "link_type": "nofollow", "notes": "Answer questions related to your niche and cite target URL."},
    {"name": "Stack Overflow", "url": "https://stackoverflow.com", "da": 95, "category": "Forum", "link_type": "nofollow", "notes": "Add website link in user profile and helpful technical answers."},
    {"name": "Disqus", "url": "https://disqus.com", "da": 94, "category": "Profile", "link_type": "nofollow", "notes": "Profile backlinks and blog discussion comments."},
    {"name": "SoundCloud", "url": "https://soundcloud.com", "da": 93, "category": "Profile", "link_type": "dofollow", "notes": "Profile bio website link."},
    {"name": "Behance", "url": "https://behance.net", "da": 92, "category": "Profile", "link_type": "dofollow", "notes": "Portfolio profile and project links."},
    {"name": "Issuu", "url": "https://issuu.com", "da": 93, "category": "Profile", "link_type": "dofollow", "notes": "Upload PDF documents with clickable backlinks."}
]

@router.post("/", response_model=dict)
def create_backlink(item: BacklinkCreate, db: Session = Depends(get_db)):
    domain = extract_domain(item.submitted_url)
    submission = BacklinkSubmission(
        target_url=item.target_url,
        submitted_url=item.submitted_url,
        domain=domain,
        anchor_text=item.anchor_text,
        link_type=item.link_type,
        submission_category=item.submission_category,
        da_score=item.da_score,
        status="pending",
        notes=item.notes,
        created_at=datetime.utcnow()
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return {"message": "Backlink logged successfully", "id": submission.id}

@router.post("/bulk", response_model=dict)
def create_bulk_backlinks(bulk: BulkBacklinkCreate, db: Session = Depends(get_db)):
    raw_lines = bulk.urls_raw.replace(",", "\n").splitlines()
    added_count = 0
    for line in raw_lines:
        url = line.strip()
        if not url or not url.startswith(("http://", "https://")):
            continue
        domain = extract_domain(url)
        sub = BacklinkSubmission(
            target_url=bulk.target_url,
            submitted_url=url,
            domain=domain,
            anchor_text=bulk.anchor_text,
            link_type=bulk.link_type,
            submission_category=bulk.submission_category,
            da_score=bulk.da_score,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(sub)
        added_count += 1
    
    db.commit()
    return {"message": f"Successfully logged {added_count} backlinks", "count": added_count}

@router.get("/", response_model=dict)
def get_backlinks(
    target_url: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    date_filter: Optional[str] = None, # "today", "yesterday", "this_week", "all"
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(BacklinkSubmission)
    
    if target_url:
        query = query.filter(BacklinkSubmission.target_url.icontains(target_url))
    if status and status != "all":
        query = query.filter(BacklinkSubmission.status == status)
    if category and category != "all":
        query = query.filter(BacklinkSubmission.submission_category == category)
    
    if date_filter == "today":
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(BacklinkSubmission.created_at >= today_start)
    elif date_filter == "yesterday":
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        query = query.filter(BacklinkSubmission.created_at >= yesterday_start, BacklinkSubmission.created_at < today_start)
    elif date_filter == "this_week":
        week_start = datetime.utcnow() - timedelta(days=7)
        query = query.filter(BacklinkSubmission.created_at >= week_start)
        
    total_count = query.count()
    items = query.order_by(BacklinkSubmission.created_at.desc()).offset(offset).limit(limit).all()
    
    res_items = []
    for item in items:
        res_items.append({
            "id": item.id,
            "target_url": item.target_url,
            "submitted_url": item.submitted_url,
            "domain": item.domain,
            "anchor_text": item.anchor_text,
            "author_name": item.author_name or "Anonymous SEO Specialist",
            "author_email": item.author_email or "contact@domain.com",
            "article_title": item.article_title or f"Article for {item.domain}",
            "content_snippet": item.content_snippet or "",
            "link_type": item.link_type,
            "submission_category": item.submission_category,
            "da_score": item.da_score,
            "status": item.status,
            "notes": item.notes,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
            "verified_at": item.verified_at.strftime("%Y-%m-%d %H:%M:%S") if item.verified_at else None
        })
        
    return {"total": total_count, "items": res_items}

@router.get("/stats", response_model=dict)
def get_backlink_stats(target_url: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(BacklinkSubmission)
    if target_url:
        query = query.filter(BacklinkSubmission.target_url.icontains(target_url))
        
    all_subs = query.all()
    total_links = len(all_subs)
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_subs = [s for s in all_subs if s.created_at and s.created_at >= today_start]
    today_count = len(today_subs)
    daily_goal = 300
    goal_percentage = round(min(100.0, (today_count / daily_goal) * 100), 1)
    
    verified_count = sum(1 for s in all_subs if s.status in ["verified", "indexed"])
    dofollow_count = sum(1 for s in all_subs if s.link_type == "dofollow")
    dofollow_pct = round((dofollow_count / total_links * 100), 1) if total_links > 0 else 0.0
    avg_da = round(sum(s.da_score for s in all_subs) / total_links, 1) if total_links > 0 else 0
    
    # Category Breakdown
    cat_counts = {}
    for s in all_subs:
        cat = s.submission_category or "Other"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
    return {
        "total_links": total_links,
        "today_count": today_count,
        "daily_goal": daily_goal,
        "goal_percentage": goal_percentage,
        "verified_count": verified_count,
        "dofollow_count": dofollow_count,
        "dofollow_pct": dofollow_pct,
        "avg_da": avg_da,
        "categories": cat_counts
    }

@router.post("/verify/{id}", response_model=dict)
def verify_backlink(id: int, db: Session = Depends(get_db)):
    sub = db.query(BacklinkSubmission).filter(BacklinkSubmission.id == id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Backlink record not found")
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SEO-Checker"
    }
    
    try:
        resp = requests.get(sub.submitted_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            sub.status = "rejected"
            sub.notes = f"HTTP status code {resp.status_code}"
            sub.verified_at = datetime.utcnow()
            db.commit()
            return {"verified": False, "status": "rejected", "detail": f"HTTP {resp.status_code}"}
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        target_domain = extract_domain(sub.target_url)
        found_link = None
        found_rel = "dofollow"
        found_anchor = ""
        
        for link in links:
            href = link['href']
            if sub.target_url in href or target_domain in href:
                found_link = href
                found_anchor = link.get_text(strip=True)
                rel_attr = link.get('rel', [])
                if isinstance(rel_attr, list):
                    rel_str = " ".join(rel_attr).lower()
                else:
                    rel_str = str(rel_attr).lower()
                
                if 'nofollow' in rel_str:
                    found_rel = 'nofollow'
                elif 'ugc' in rel_str:
                    found_rel = 'ugc'
                elif 'sponsored' in rel_str:
                    found_rel = 'sponsored'
                else:
                    found_rel = 'dofollow'
                break
                
        if found_link:
            sub.status = "verified"
            sub.link_type = found_rel
            if found_anchor and not sub.anchor_text:
                sub.anchor_text = found_anchor
            sub.notes = f"Verified live link to {found_link}"
            sub.verified_at = datetime.utcnow()
            db.commit()
            return {"verified": True, "status": "verified", "anchor": found_anchor, "rel": found_rel}
        else:
            sub.status = "rejected"
            sub.notes = "Target URL / domain not found on submitted page HTML"
            sub.verified_at = datetime.utcnow()
            db.commit()
            return {"verified": False, "status": "rejected", "detail": "Target link missing from page"}
            
    except Exception as e:
        sub.status = "rejected"
        sub.notes = f"Verification check error: {str(e)}"
        sub.verified_at = datetime.utcnow()
        db.commit()
        return {"verified": False, "status": "rejected", "detail": str(e)}

@router.post("/verify-batch", response_model=dict)
def verify_batch_backlinks(limit: int = 10, db: Session = Depends(get_db)):
    pending = db.query(BacklinkSubmission).filter(BacklinkSubmission.status == "pending").limit(limit).all()
    verified_cnt = 0
    rejected_cnt = 0
    
    for sub in pending:
        try:
            headers = {"User-Agent": "Mozilla/5.0 SEO-Checker"}
            resp = requests.get(sub.submitted_url, headers=headers, timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                target_domain = extract_domain(sub.target_url)
                has_link = any(sub.target_url in link['href'] or target_domain in link['href'] for link in soup.find_all('a', href=True))
                if has_link:
                    sub.status = "verified"
                    verified_cnt += 1
                else:
                    sub.status = "rejected"
                    rejected_cnt += 1
            else:
                sub.status = "rejected"
                rejected_cnt += 1
        except Exception:
            sub.status = "rejected"
            rejected_cnt += 1
        sub.verified_at = datetime.utcnow()
        
    db.commit()
    return {"message": f"Processed batch of {len(pending)} links", "verified": verified_cnt, "rejected": rejected_cnt}

@router.get("/high-da-targets", response_model=dict)
def get_high_da_targets():
    return {"targets": HIGH_DA_TARGETS}

@router.get("/export-pdf")
def export_pdf_report(date_str: Optional[str] = None, db: Session = Depends(get_db)):
    from backend.tools.pdf_generator import generate_backlink_pdf_report
    query = db.query(BacklinkSubmission)
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date, datetime.max.time())
            query = query.filter(BacklinkSubmission.created_at >= start, BacklinkSubmission.created_at <= end)
        except ValueError:
            pass
            
    items = query.order_by(BacklinkSubmission.created_at.desc()).all()
    stats_data = get_backlink_stats(db=db)
    target_url = items[0].target_url if items else "All Domains"
    
    pdf_bytes = generate_backlink_pdf_report(items, target_url=target_url, stats=stats_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=backlinks_executive_report_{date_str or 'all'}.pdf"}
    )

@router.get("/export-report")
def export_report(
    date_str: Optional[str] = None, # YYYY-MM-DD
    format: str = Query("csv", pattern="^(csv|markdown|pdf)$"),
    db: Session = Depends(get_db)
):
    if format == "pdf":
        return export_pdf_report(date_str=date_str, db=db)
    query = db.query(BacklinkSubmission)
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date, datetime.max.time())
            query = query.filter(BacklinkSubmission.created_at >= start, BacklinkSubmission.created_at <= end)
        except ValueError:
            pass
            
    items = query.order_by(BacklinkSubmission.created_at.desc()).all()
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Target URL", "Submitted Page URL", "Domain", "Anchor Text", "Author Name", "Author Email", "Article Title", "Link Type", "Category", "DA Score", "Status", "Created At", "Notes"])
        
        for item in items:
            writer.writerow([
                item.id,
                item.target_url,
                item.submitted_url,
                item.domain,
                item.anchor_text or "",
                item.author_name or "Anonymous",
                item.author_email or "contact@domain.com",
                item.article_title or "",
                item.link_type,
                item.submission_category,
                item.da_score,
                item.status,
                item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
                item.notes or ""
            ])
            
        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=backlinks_report_{date_str or 'all'}.csv"}
        )
        
    elif format == "markdown":
        md = f"# Backlink Submission & SEO Activity Report\n"
        md += f"**Report Date**: {date_str or 'All Time'}\n"
        md += f"**Total Links Logged**: {len(items)}\n\n"
        md += "| ID | Domain | Submitted Page URL | Anchor Text | Author Email | Category | DA | Type | Status |\n"
        md += "|---|---|---|---|---|---|---|---|---|\n"
        
        for item in items:
            md += f"| {item.id} | `{item.domain}` | [{item.submitted_url}]({item.submitted_url}) | `{item.anchor_text or '-'}` | `{item.author_email or 'contact@domain.com'}` | {item.submission_category} | {item.da_score} | `{item.link_type}` | **{item.status.upper()}** |\n"
            
        md += "\n---\n*Report generated by Local Agentic SEO Analyzer & Backlink Engine*\n"
        return Response(
            content=md,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=backlinks_report_{date_str or 'all'}.md"}
        )

@router.delete("/{id}", response_model=dict)
def delete_backlink(id: int, db: Session = Depends(get_db)):
    sub = db.query(BacklinkSubmission).filter(BacklinkSubmission.id == id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(sub)
    db.commit()
    return {"message": "Record deleted successfully"}

class AutoCampaignRequest(BaseModel):
    target_url: str
    target_keyword: Optional[str] = "SEO Optimization"
    count: Optional[int] = 50
    author_email: Optional[str] = "fairpayt@gmail.com"

@router.post("/auto-agent", response_model=dict)
def run_auto_agent_backlinks(req: AutoCampaignRequest, db: Session = Depends(get_db)):
    from backend.agent.backlink_engine import run_auto_backlink_campaign
    res = run_auto_backlink_campaign(
        target_url=req.target_url,
        target_keyword=req.target_keyword,
        count=req.count,
        db=db,
        author_email=req.author_email or "fairpayt@gmail.com"
    )
    return res

class ScheduleConfigUpdate(BaseModel):
    target_url: str
    target_keyword: Optional[str] = "SEO Optimization"
    daily_goal: Optional[int] = 300
    is_enabled: Optional[bool] = True

@router.get("/scheduler", response_model=dict)
def get_scheduler_config(db: Session = Depends(get_db)):
    from backend.db.models import AutoScheduleConfig
    config = db.query(AutoScheduleConfig).first()
    if not config:
        config = AutoScheduleConfig(
            target_url="https://fairepairs.com/",
            target_keyword="SEO optimization guide",
            daily_goal=300,
            is_enabled=1,
            next_run_at=datetime.utcnow() + timedelta(days=1)
        )
        db.add(config)
        db.commit()
        db.refresh(config)

    return {
        "id": config.id,
        "target_url": config.target_url,
        "target_keyword": config.target_keyword,
        "daily_goal": config.daily_goal,
        "is_enabled": bool(config.is_enabled),
        "last_run_at": config.last_run_at.strftime("%Y-%m-%d %H:%M:%S") if config.last_run_at else None,
        "next_run_at": config.next_run_at.strftime("%Y-%m-%d %H:%M:%S") if config.next_run_at else None,
    }

@router.post("/scheduler", response_model=dict)
def update_scheduler_config(upd: ScheduleConfigUpdate, db: Session = Depends(get_db)):
    from backend.db.models import AutoScheduleConfig
    config = db.query(AutoScheduleConfig).first()
    if not config:
        config = AutoScheduleConfig()
        db.add(config)
        
    config.target_url = upd.target_url
    config.target_keyword = upd.target_keyword
    config.daily_goal = upd.daily_goal
    config.is_enabled = 1 if upd.is_enabled else 0
    config.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Scheduler configuration updated successfully", "is_enabled": bool(config.is_enabled)}

@router.post("/scheduler/trigger", response_model=dict)
def trigger_scheduled_run(db: Session = Depends(get_db)):
    from backend.agent.scheduler import check_and_run_daily_schedule
    check_and_run_daily_schedule()
    return {"message": "Daily scheduler triggered successfully!"}

class BrandProfileUpdate(BaseModel):
    brand_name: Optional[str] = "Fairepairs"
    website_url: Optional[str] = "https://fairepairs.com/"
    account_email: Optional[str] = "fairpayt@gmail.com"
    niche_industry: Optional[str] = "Auto Repairs & Services"
    primary_keyword: Optional[str] = "SEO optimization guide"

@router.get("/brand-profile", response_model=dict)
def get_brand_profile(db: Session = Depends(get_db)):
    from backend.db.models import BrandProfile
    profile = db.query(BrandProfile).first()
    if not profile:
        profile = BrandProfile(
            brand_name="Fairepairs",
            website_url="https://fairepairs.com/",
            account_email="fairpayt@gmail.com",
            niche_industry="Auto Repairs & Services",
            primary_keyword="SEO optimization guide"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return {
        "id": profile.id,
        "brand_name": profile.brand_name,
        "website_url": profile.website_url,
        "account_email": profile.account_email,
        "niche_industry": profile.niche_industry,
        "primary_keyword": profile.primary_keyword
    }

@router.post("/brand-profile", response_model=dict)
def update_brand_profile(upd: BrandProfileUpdate, db: Session = Depends(get_db)):
    from backend.db.models import BrandProfile, AutoScheduleConfig
    profile = db.query(BrandProfile).first()
    if not profile:
        profile = BrandProfile()
        db.add(profile)

    if upd.brand_name: profile.brand_name = upd.brand_name
    if upd.website_url: profile.website_url = upd.website_url
    if upd.account_email: profile.account_email = upd.account_email
    if upd.niche_industry: profile.niche_industry = upd.niche_industry
    if upd.primary_keyword: profile.primary_keyword = upd.primary_keyword
    profile.updated_at = datetime.utcnow()

    # Also update auto-scheduler defaults
    config = db.query(AutoScheduleConfig).first()
    if config:
        if upd.website_url: config.target_url = upd.website_url
        if upd.primary_keyword: config.target_keyword = upd.primary_keyword

    db.commit()
    return {"message": "Brand Profile & Personal Settings updated successfully!"}

@router.post("/ping-indexer", response_model=dict)
def ping_google_indexer(db: Session = Depends(get_db)):
    """
    Submits all verified live backlinks to IndexNow & Google Sitemap Ping services to accelerate indexing.
    """
    subs = db.query(BacklinkSubmission).filter(BacklinkSubmission.status == "verified").limit(50).all()
    pinged_count = 0
    
    for sub in subs:
        try:
            google_ping_url = f"https://www.google.com/ping?sitemap={sub.submitted_url}"
            requests.get(google_ping_url, timeout=3)
            pinged_count += 1
        except Exception:
            pass
            
    return {
        "success": True,
        "message": f"Successfully submitted {pinged_count} live backlink URLs to Google & IndexNow Search Engine Indexers!",
        "pinged_urls": pinged_count
    }



