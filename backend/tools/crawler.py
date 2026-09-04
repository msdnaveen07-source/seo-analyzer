import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AgenticSEOBot/1.0"

class DocumentFetcher:
    def __init__(self, user_agent=DEFAULT_USER_AGENT):
        self.user_agent = user_agent
        self.headers = {"User-Agent": self.user_agent}

    def fetch(self, target: str, use_js: bool = False) -> dict:
        """
        Fetches document content from local file path or web URL.
        Returns dict with status, html, headers, final_url, is_local.
        """
        if os.path.exists(target):
            try:
                with open(target, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                return {
                    "success": True,
                    "is_local": True,
                    "target": target,
                    "html": content,
                    "status_code": 200,
                    "headers": {},
                    "final_url": target,
                }
            except Exception as e:
                return {
                    "success": False,
                    "is_local": True,
                    "target": target,
                    "error": str(e),
                    "html": "",
                    "status_code": 500,
                }

        # Remote URL
        parsed = urlparse(target)
        if not parsed.scheme:
            target = "https://" + target

        if use_js:
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page(user_agent=self.user_agent)
                    response = page.goto(target, timeout=30000, wait_until="networkidle")
                    content = page.content()
                    status = response.status if response else 200
                    browser.close()
                    return {
                        "success": True,
                        "is_local": False,
                        "target": target,
                        "html": content,
                        "status_code": status,
                        "headers": {},
                        "final_url": target,
                    }
            except Exception as js_err:
                print(f"Playwright fetch fallback to requests: {js_err}")

        try:
            resp = requests.get(target, headers=self.headers, timeout=15, allow_redirects=True)
            return {
                "success": resp.status_code == 200,
                "is_local": False,
                "target": target,
                "html": resp.text,
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "final_url": resp.url,
            }
        except Exception as e:
            return {
                "success": False,
                "is_local": False,
                "target": target,
                "error": str(e),
                "html": "",
                "status_code": 0,
                "headers": {},
                "final_url": target,
            }

    def fetch_robots_txt(self, base_url: str) -> dict:
        if os.path.exists(base_url):
            return {"exists": False, "content": "Local file audit", "allowed": True}
        
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            resp = requests.get(robots_url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return {"exists": True, "content": resp.text, "url": robots_url}
        except Exception:
            pass
        return {"exists": False, "content": "", "url": robots_url}

    def fetch_sitemap(self, base_url: str) -> dict:
        if os.path.exists(base_url):
            return {"exists": False, "urls": []}

        parsed = urlparse(base_url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        try:
            resp = requests.get(sitemap_url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                urls = []
                for child in root:
                    for sub in child:
                        if sub.tag.endswith("loc"):
                            urls.append(sub.text)
                return {"exists": True, "urls": urls, "url": sitemap_url}
        except Exception:
            pass
        return {"exists": False, "urls": [], "url": sitemap_url}
