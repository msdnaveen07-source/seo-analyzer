from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from backend.tools.scrapegraph import (
    scrape_url_to_markdown,
    extract_structured_data_from_url,
    search_scrapegraphai,
    crawl_scrapegraphai,
    monitor_scrapegraphai
)

router = APIRouter(prefix="/api/scrape", tags=["scrapegraph"])

class MarkdownRequest(BaseModel):
    url: str
    sgai_api_key: Optional[str] = None

class ExtractRequest(BaseModel):
    url: str
    prompt: str
    sgai_api_key: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    prompt: Optional[str] = "Extract top insights"
    num_results: Optional[int] = 3
    location_geocode: Optional[str] = "us"
    sgai_api_key: Optional[str] = None

class CrawlRequest(BaseModel):
    url: str
    sgai_api_key: Optional[str] = None
    max_pages: Optional[int] = 5

class MonitorRequest(BaseModel):
    url: str
    interval: Optional[str] = "0 */6 * * *"
    webhook_url: Optional[str] = None
    sgai_api_key: Optional[str] = None

@router.post("/markdown")
def convert_to_markdown(req: MarkdownRequest):
    """Convert any webpage URL into clean Markdown for LLMs."""
    if not req.url or not req.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL provided")
    result = scrape_url_to_markdown(url=req.url, api_key=req.sgai_api_key)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Conversion failed"))
    return result

@router.post("/extract")
def extract_structured(req: ExtractRequest):
    """Extract structured JSON data using natural language prompts."""
    if not req.url or not req.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL provided")
    result = extract_structured_data_from_url(url=req.url, prompt=req.prompt, api_key=req.sgai_api_key)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Extraction failed"))
    return result

@router.post("/search")
def search_insights(req: SearchRequest):
    """Search web and extract structured trends via ScrapeGraphAI Search API."""
    if not req.query:
        raise HTTPException(status_code=400, detail="Search query required")
    result = search_scrapegraphai(
        query=req.query,
        prompt=req.prompt or "Extract top insights",
        num_results=req.num_results or 3,
        location_geocode=req.location_geocode or "us",
        api_key=req.sgai_api_key
    )
    return result

@router.post("/crawl")
def crawl_website(req: CrawlRequest):
    """Crawl pages across a site or domain."""
    if not req.url or not req.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL provided")
    result = crawl_scrapegraphai(url=req.url, api_key=req.sgai_api_key, max_pages=req.max_pages or 5)
    return result

@router.post("/monitor")
def monitor_page(req: MonitorRequest):
    """Watch webpage for changes via webhook or snapshot hash."""
    if not req.url or not req.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL provided")
    result = monitor_scrapegraphai(
        url=req.url,
        interval=req.interval or "0 */6 * * *",
        webhook_url=req.webhook_url,
        api_key=req.sgai_api_key
    )
    return result
