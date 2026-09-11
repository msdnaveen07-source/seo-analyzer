import os
import re
import json
import hashlib
import requests
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

SGAI_BASE_URL = "https://v2-api.scrapegraphai.com/api"

def get_sgai_api_key(passed_key: Optional[str] = None) -> Optional[str]:
    """Returns passed API key or fetches SGAI_API_KEY from environment variables."""
    key = passed_key or os.getenv("SGAI_API_KEY")
    if key and key.strip():
        return key.strip()
    return None

def convert_html_to_markdown(html_content: str, base_url: str = "") -> str:
    """
    Converts HTML content to clean, well-formatted Markdown.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    for element in soup(["script", "style", "svg", "noscript", "header", "footer", "iframe"]):
        element.decompose()
        
    main_content = soup.find('main') or soup.find('article') or soup.find('body') or soup
    markdown_lines = []
    
    for elem in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'blockquote', 'a', 'table']):
        name = elem.name
        text = elem.get_text(strip=True)
        if not text and name not in ['a', 'table']:
            continue
            
        if name == 'h1':
            markdown_lines.append(f"\n# {text}\n")
        elif name == 'h2':
            markdown_lines.append(f"\n## {text}\n")
        elif name == 'h3':
            markdown_lines.append(f"\n### {text}\n")
        elif name in ['h4', 'h5', 'h6']:
            markdown_lines.append(f"\n#### {text}\n")
        elif name == 'p':
            markdown_lines.append(f"\n{text}\n")
        elif name in ['ul', 'ol']:
            items = elem.find_all('li')
            for idx, li in enumerate(items, 1):
                prefix = "*" if name == 'ul' else f"{idx}."
                markdown_lines.append(f"{prefix} {li.get_text(strip=True)}")
            markdown_lines.append("")
        elif name == 'blockquote':
            markdown_lines.append(f"\n> {text}\n")
        elif name == 'pre':
            markdown_lines.append(f"\n```\n{text}\n```\n")
        elif name == 'table':
            rows = elem.find_all('tr')
            for r_idx, row in enumerate(rows):
                cols = [c.get_text(strip=True) for c in row.find_all(['td', 'th'])]
                if cols:
                    markdown_lines.append("| " + " | ".join(cols) + " |")
                    if r_idx == 0:
                        markdown_lines.append("| " + " | ".join(['---'] * len(cols)) + " |")
            markdown_lines.append("")

    return "\n".join(markdown_lines).strip()

def scrape_url_to_markdown(url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Scrapes URL to Markdown using ScrapeGraphAI v2 API if key is available, else local fallback.
    """
    sgai_key = get_sgai_api_key(api_key)
    
    # 1. Try ScrapeGraphAI v2 REST API if key exists
    if sgai_key:
        try:
            res = requests.post(
                f"{SGAI_BASE_URL}/scrape",
                headers={
                    "Content-Type": "application/json",
                    "SGAI-APIKEY": sgai_key
                },
                json={
                    "url": url,
                    "formats": [{"type": "markdown"}]
                },
                timeout=20
            )
            if res.status_code == 200:
                data = res.json()
                result_md = data.get("result") or data.get("markdown") or str(data)
                if isinstance(result_md, dict):
                    result_md = result_md.get("markdown", str(result_md))
                return {
                    "success": True,
                    "engine": "ScrapeGraphAI v2 API",
                    "url": url,
                    "title": url,
                    "markdown": result_md,
                    "word_count": len(re.findall(r'\w+', str(result_md))),
                    "char_count": len(str(result_md)),
                    "raw": data
                }
        except Exception as api_err:
            pass # Fallback to local scraper
            
    # 2. Local Fallback
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        html = response.text
        
        soup = BeautifulSoup(html, 'lxml')
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        markdown_text = convert_html_to_markdown(html, base_url=url)
        
        return {
            "success": True,
            "engine": "Local HTML Engine",
            "url": url,
            "title": title,
            "markdown": markdown_text,
            "word_count": len(re.findall(r'\w+', markdown_text)),
            "char_count": len(markdown_text)
        }
    except Exception as e:
        return {"success": False, "url": url, "error": str(e)}

def extract_structured_data_from_url(
    url: str, 
    prompt: str, 
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extracts structured JSON data using ScrapeGraphAI v2 API or Local Fallback.
    """
    sgai_key = get_sgai_api_key(api_key)
    
    # 1. Try ScrapeGraphAI v2 REST API if key exists
    if sgai_key:
        try:
            res = requests.post(
                f"{SGAI_BASE_URL}/extract",
                headers={
                    "Content-Type": "application/json",
                    "SGAI-APIKEY": sgai_key
                },
                json={
                    "url": url,
                    "prompt": prompt
                },
                timeout=25
            )
            if res.status_code == 200:
                data = res.json()
                return {
                    "success": True,
                    "engine": "ScrapeGraphAI v2 Cloud API",
                    "data": data.get("result") or data,
                    "url": url,
                    "prompt": prompt
                }
        except Exception as api_err:
            pass # Fallback
            
    # 2. Local Heuristic Extraction Fallback
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        
        contacts = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', res.text)))
        phones = list(set(re.findall(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', res.text)))
        phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 10][:5]
        
        socials = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(s in href.lower() for s in ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com', 'instagram.com', 'github.com']):
                socials.append(href)
        socials = list(set(socials))
        
        h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
        h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]
        has_submit_form = any(k in res.text.lower() for k in ['write for us', 'submit article', 'guest post', 'contribute', 'contact us'])
        
        return {
            "success": True,
            "engine": "Local Smart AI Engine",
            "data": {
                "page_title": soup.title.string.strip() if soup.title and soup.title.string else "",
                "emails_found": contacts[:10],
                "phones_found": phones,
                "social_profiles": socials,
                "primary_headings": h1s,
                "sub_headings": h2s[:8],
                "guest_post_submission_indicator": has_submit_form,
                "prompt_target": prompt,
                "summary_snippet": soup.get_text(strip=True)[:400]
            },
            "url": url,
            "prompt": prompt
        }
    except Exception as e:
        return {"success": False, "url": url, "error": str(e)}

def search_scrapegraphai(
    query: str, 
    prompt: str, 
    num_results: int = 3, 
    location_geocode: str = "us",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search web and extract structured insights using ScrapeGraphAI v2 Search API.
    """
    sgai_key = get_sgai_api_key(api_key)
    if sgai_key:
        try:
            res = requests.post(
                f"{SGAI_BASE_URL}/search",
                headers={
                    "Content-Type": "application/json",
                    "SGAI-APIKEY": sgai_key
                },
                json={
                    "query": query,
                    "numResults": num_results,
                    "prompt": prompt,
                    "locationGeoCode": location_geocode
                },
                timeout=30
            )
            if res.status_code == 200:
                data = res.json()
                return {
                    "success": True,
                    "engine": "ScrapeGraphAI v2 Search API",
                    "data": data.get("result") or data,
                    "query": query
                }
        except Exception as e:
            return {"success": False, "query": query, "error": str(e)}

    return {
        "success": False,
        "query": query,
        "error": "SGAI_API_KEY required for ScrapeGraphAI Search API"
    }

def crawl_scrapegraphai(url: str, api_key: Optional[str] = None, max_pages: int = 5) -> Dict[str, Any]:
    """
    Crawl site using ScrapeGraphAI v2 Crawl API or Local Crawler fallback.
    """
    sgai_key = get_sgai_api_key(api_key)
    if sgai_key:
        try:
            res = requests.post(
                f"{SGAI_BASE_URL}/crawl",
                headers={
                    "Content-Type": "application/json",
                    "SGAI-APIKEY": sgai_key
                },
                json={"url": url},
                timeout=30
            )
            if res.status_code == 200:
                data = res.json()
                return {
                    "success": True,
                    "engine": "ScrapeGraphAI v2 Crawl API",
                    "data": data.get("result") or data,
                    "start_url": url
                }
        except Exception as e:
            pass

    # Local crawler fallback
    domain = urlparse(url).netloc
    visited = set()
    to_visit = [url]
    results = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    while to_visit and len(visited) < max_pages:
        curr_url = to_visit.pop(0)
        if curr_url in visited:
            continue
        visited.add(curr_url)
        try:
            res = requests.get(curr_url, headers=headers, timeout=8)
            if res.status_code != 200:
                continue
            soup = BeautifulSoup(res.text, 'lxml')
            title = soup.title.string.strip() if soup.title and soup.title.string else curr_url
            
            for a in soup.find_all('a', href=True):
                full_link = urljoin(curr_url, a['href'])
                if urlparse(full_link).netloc == domain and full_link not in visited and full_link not in to_visit:
                    if len(to_visit) < 15:
                        to_visit.append(full_link)
                        
            results.append({
                "url": curr_url,
                "title": title,
                "word_count": len(re.findall(r'\w+', res.text)),
                "snippet": convert_html_to_markdown(res.text)[:400]
            })
        except Exception:
            continue
            
    return {
        "success": True,
        "engine": "Local Multi-Page Crawler",
        "start_url": url,
        "total_crawled": len(results),
        "pages": results
    }

def monitor_scrapegraphai(
    url: str, 
    interval: str = "0 */6 * * *", 
    webhook_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Setup page monitoring with ScrapeGraphAI v2 Monitor API or Local Snapshot check.
    """
    sgai_key = get_sgai_api_key(api_key)
    if sgai_key:
        try:
            payload = {
                "url": url,
                "interval": interval,
                "formats": [{"type": "markdown"}]
            }
            if webhook_url:
                payload["webhookUrl"] = webhook_url
                
            res = requests.post(
                f"{SGAI_BASE_URL}/monitor",
                headers={
                    "Content-Type": "application/json",
                    "SGAI-APIKEY": sgai_key
                },
                json=payload,
                timeout=20
            )
            if res.status_code == 200:
                data = res.json()
                return {
                    "success": True,
                    "engine": "ScrapeGraphAI v2 Monitor API",
                    "data": data.get("result") or data,
                    "url": url
                }
        except Exception as e:
            pass

    # Local snapshot fallback
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        meta_desc = ""
        meta_elem = soup.find('meta', attrs={'name': re.compile(r'description', re.I)})
        if meta_elem:
            meta_desc = meta_elem.get('content', '')
            
        clean_text = soup.get_text(strip=True)
        content_hash = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()
        
        return {
            "success": True,
            "engine": "Local Snapshot Monitor",
            "url": url,
            "status_code": res.status_code,
            "title": title,
            "meta_description": meta_desc,
            "content_hash": content_hash,
            "content_length": len(clean_text)
        }
    except Exception as e:
        return {"success": False, "url": url, "error": str(e)}
