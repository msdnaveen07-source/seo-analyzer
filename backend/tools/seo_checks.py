import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import textstat

class SEOChecker:
    def __init__(self, html: str, target_url: str, keyword: str = "", sitemap_urls: list = None):
        self.soup = BeautifulSoup(html, "html.parser")
        self.raw_html = html
        self.target_url = target_url
        self.keyword = (keyword or "").strip().lower()
        self.sitemap_urls = sitemap_urls or []
        self.parsed_url = urlparse(target_url) if target_url.startswith("http") else None

    def run_all_checks(self) -> list:
        checks = [
            self.check_title(),
            self.check_meta_description(),
            self.check_headings(),
            self.check_url_structure(),
            self.check_content_and_readability(),
            self.check_images(),
            self.check_internal_links(),
            self.check_external_links(),
            self.check_technical(),
        ]
        return checks

    # 1. Title Tag Check
    def check_title(self) -> dict:
        title_tag = self.soup.find("title")
        title_text = title_tag.string.strip() if (title_tag and title_tag.string) else ""
        
        if not title_text:
            return {
                "id": "title_tag",
                "category": "Title & Meta",
                "name": "Title Tag Existence & Quality",
                "status": "fail",
                "score": 0,
                "message": "Title tag is missing or empty.",
                "details": {"current_title": "", "length": 0},
                "fixable": True,
                "recommendation": f"Add a title tag between 50-60 characters containing '{self.keyword or 'primary keyword'}'.",
            }

        length = len(title_text)
        kw_in_title = self.keyword in title_text.lower() if self.keyword else True
        kw_near_start = (title_text.lower().find(self.keyword) <= 20) if (self.keyword and kw_in_title) else False

        status = "pass"
        score = 100
        issues = []

        if length < 50 or length > 60:
            status = "warn"
            score -= 30
            issues.append(f"Length is {length} chars (optimal is 50-60).")

        if self.keyword and not kw_in_title:
            status = "fail"
            score -= 50
            issues.append(f"Primary keyword '{self.keyword}' not found in title.")
        elif self.keyword and not kw_near_start:
            score -= 10
            issues.append("Primary keyword is not near the beginning of the title.")

        msg = f"Title tag present: '{title_text}' ({length} chars)."
        if issues:
            msg += " " + " ".join(issues)

        return {
            "id": "title_tag",
            "category": "Title & Meta",
            "name": "Title Tag Existence & Quality",
            "status": status,
            "score": max(0, score),
            "message": msg,
            "details": {
                "title": title_text,
                "length": length,
                "has_keyword": kw_in_title,
                "keyword_near_start": kw_near_start,
            },
            "fixable": True,
            "recommendation": f"Optimize title to 50-60 characters with '{self.keyword or 'primary keyword'}' at the front.",
        }

    # 2. Meta Description Check
    def check_meta_description(self) -> dict:
        meta_desc = self.soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        desc_text = meta_desc.get("content", "").strip() if meta_desc else ""

        if not desc_text:
            return {
                "id": "meta_description",
                "category": "Title & Meta",
                "name": "Meta Description Check",
                "status": "fail",
                "score": 0,
                "message": "Meta description is missing.",
                "details": {"current_meta": "", "length": 0},
                "fixable": True,
                "recommendation": f"Add a compelling meta description (150-160 chars) including '{self.keyword or 'primary keyword'}' and a Call To Action (CTA).",
            }

        length = len(desc_text)
        kw_present = self.keyword in desc_text.lower() if self.keyword else True
        cta_words = ["learn", "discover", "get", "try", "buy", "find out", "check", "explore", "read", "click", "download", "contact", "start", "sign up", "order"]
        has_cta = any(w in desc_text.lower() for w in cta_words)

        status = "pass"
        score = 100
        issues = []

        if length < 150 or length > 160:
            status = "warn"
            score -= 25
            issues.append(f"Length is {length} chars (target: 150-160 chars).")

        if self.keyword and not kw_present:
            status = "warn"
            score -= 30
            issues.append(f"Keyword '{self.keyword}' not found in meta description.")

        if not has_cta:
            score -= 15
            issues.append("No clear Call-to-Action (CTA) phrase detected.")

        msg = f"Meta description found ({length} chars)."
        if issues:
            msg += " " + " ".join(issues)

        return {
            "id": "meta_description",
            "category": "Title & Meta",
            "name": "Meta Description Check",
            "status": status,
            "score": max(0, score),
            "message": msg,
            "details": {
                "meta_description": desc_text,
                "length": length,
                "has_keyword": kw_present,
                "has_cta": has_cta,
            },
            "fixable": True,
            "recommendation": "Craft meta description of 150-160 characters containing primary keyword and action verb.",
        }

    # 3. Headings Structure Check
    def check_headings(self) -> dict:
        h1s = self.soup.find_all("h1")
        h2s = self.soup.find_all("h2")
        h3s = self.soup.find_all("h3")

        status = "pass"
        score = 100
        issues = []

        if len(h1s) == 0:
            status = "fail"
            score -= 50
            issues.append("Missing H1 heading.")
        elif len(h1s) > 1:
            status = "warn"
            score -= 25
            issues.append(f"Multiple H1 headings found ({len(h1s)}). Page should have exactly one H1.")

        h1_text = h1s[0].get_text().strip() if h1s else ""
        if self.keyword and h1_text and (self.keyword not in h1_text.lower()):
            status = "warn"
            score -= 25
            issues.append(f"Primary keyword '{self.keyword}' is not in H1 ('{h1_text}').")

        # Hierarchy check: check if H3 exists without H2
        if len(h3s) > 0 and len(h2s) == 0:
            status = "warn"
            score -= 20
            issues.append("H3 headings exist without any preceding H2 headings (broken hierarchy).")

        msg = f"Headings: {len(h1s)} H1, {len(h2s)} H2, {len(h3s)} H3."
        if issues:
            msg += " " + " ".join(issues)

        return {
            "id": "headings_structure",
            "category": "Content & Structure",
            "name": "Headings Hierarchy (H1-H3)",
            "status": status,
            "score": max(0, score),
            "message": msg,
            "details": {
                "h1_count": len(h1s),
                "h2_count": len(h2s),
                "h3_count": len(h3s),
                "h1_text": h1_text,
            },
            "fixable": True,
            "recommendation": "Ensure exactly one H1 with primary keyword, followed logically by H2 and H3 tags.",
        }

    # 4. URL Structure Check
    def check_url_structure(self) -> dict:
        if not self.parsed_url:
            return {
                "id": "url_structure",
                "category": "Technical",
                "name": "URL Structure Analysis",
                "status": "pass",
                "score": 100,
                "message": "Local file path audit - URL structure check skipped.",
                "details": {"is_local": True},
                "fixable": False,
                "recommendation": "N/A for local files.",
            }

        path = self.parsed_url.path
        query = self.parsed_url.query

        status = "pass"
        score = 100
        issues = []

        if len(path) > 75:
            status = "warn"
            score -= 20
            issues.append("URL path is unusually long (>75 chars).")

        if query:
            status = "warn"
            score -= 20
            issues.append("URL contains query string clutter.")

        if "_" in path:
            score -= 10
            issues.append("URL contains underscores instead of hyphens.")

        if self.keyword:
            clean_kw = re.sub(r"[^\w\s-]", "", self.keyword).strip().replace(" ", "-")
            if clean_kw not in path.lower() and self.keyword not in path.lower():
                score -= 25
                issues.append(f"URL slug does not contain keyword '{self.keyword}'.")

        msg = f"URL path: '{path}'."
        if issues:
            msg += " " + " ".join(issues)

        return {
            "id": "url_structure",
            "category": "Technical",
            "name": "URL Structure Analysis",
            "status": status,
            "score": max(0, score),
            "message": msg,
            "details": {"path": path, "query": query, "length": len(self.target_url)},
            "fixable": False,
            "recommendation": "Use short, hyphen-separated URLs containing your primary target keyword.",
        }

    # 5. Content, Keyword Density & Readability Check
    def check_content_and_readability(self) -> dict:
        # Extract visible text
        for element in self.soup(["script", "style", "nav", "footer", "header"]):
            element.extract()
        
        text = self.soup.get_text(separator=" ")
        words = re.findall(r"\b\w+\b", text.lower())
        word_count = len(words)

        # Keyword density
        kw_count = 0
        kw_density = 0.0
        if self.keyword and word_count > 0:
            kw_words = self.keyword.split()
            if len(kw_words) == 1:
                kw_count = words.count(self.keyword)
            else:
                kw_count = len(re.findall(re.escape(self.keyword), text.lower()))
            kw_density = round((kw_count * len(kw_words) / word_count) * 100, 2)

        # Readability score via textstat
        readability_score = textstat.flesch_reading_ease(text) if text.strip() else 0
        grade_level = textstat.flesch_kincaid_grade(text) if text.strip() else 0

        status = "pass"
        score = 100
        issues = []

        if word_count < 300:
            status = "fail"
            score -= 40
            issues.append(f"Thin content: only {word_count} words (minimum recommended: 300-600 words).")
        elif word_count < 600:
            status = "warn"
            score -= 15
            issues.append(f"Word count is {word_count} (recommended: 600+ words).")

        if self.keyword:
            if kw_density == 0:
                status = "fail"
                score -= 30
                issues.append(f"Keyword '{self.keyword}' does not appear in body text.")
            elif kw_density > 3.0:
                status = "warn"
                score -= 20
                issues.append(f"High keyword density ({kw_density}%), risk of keyword stuffing (target 1-2.5%).")

        if readability_score < 50:
            status = "warn" if status == "pass" else status
            score -= 15
            issues.append(f"Readability is difficult (Flesch score: {readability_score:.1f}, Grade {grade_level}). Target grade: 7-8.")

        msg = f"Word count: {word_count}. Readability: {readability_score:.1f} (Grade {grade_level}). Keyword density: {kw_density}%."
        if issues:
            msg += " " + " ".join(issues)

        return {
            "id": "content_readability",
            "category": "Content & Structure",
            "name": "Content Word Count, Density & Readability",
            "status": status,
            "score": max(0, score),
            "message": msg,
            "details": {
                "word_count": word_count,
                "keyword_count": kw_count,
                "keyword_density_pct": kw_density,
                "flesch_reading_ease": readability_score,
                "flesch_grade": grade_level,
            },
            "fixable": True,
            "recommendation": "Aim for 600+ words, maintain 1-2.5% keyword density, and keep readability at grade 7-8.",
        }

    # 6. Images Check
    def check_images(self) -> dict:
        imgs = self.soup.find_all("img")
        if not imgs:
            return {
                "id": "images_check",
                "category": "Media",
                "name": "Image Alt & Optimization Check",
                "status": "pass",
                "score": 100,
                "message": "No images found on page.",
                "details": {"total_images": 0},
                "fixable": False,
                "recommendation": "Consider adding relevant images with descriptive alt text.",
            }

        missing_alt = []
        lazy_count = 0
        webp_count = 0

        for img in imgs:
            alt = img.get("alt")
            src = img.get("src", "")
            loading = img.get("loading", "")

            if alt is None or not alt.strip():
                missing_alt.append(src)
            
            if loading == "lazy":
                lazy_count += 1

            if src.lower().endswith((".webp", ".avif")):
                webp_count += 1

        total = len(imgs)
        missing_count = len(missing_alt)
        status = "pass"
        score = 100
        issues = []

        if missing_count > 0:
            status = "fail" if (missing_count / total > 0.5) else "warn"
            score -= min(50, missing_count * 15)
            issues.append(f"{missing_count}/{total} images missing alt text.")

        if total > 2 and lazy_count == 0:
            score -= 10
            issues.append("No lazy-loading attributes ('loading=\"lazy\"') found on images.")

        if total > 0 and webp_count == 0:
            score -= 10
            issues.append("No next-gen image formats (WebP/AVIF) detected.")

        msg = f"{total} images found. {total - missing_count}/{total} have alt text. {lazy_count} lazy-loaded."
        if issues:
            msg += " " + " ".join(issues)

        return {
            "id": "images_check",
            "category": "Media",
            "name": "Image Alt & Optimization Check",
            "status": status,
            "score": max(0, score),
            "message": msg,
            "details": {
                "total_images": total,
                "missing_alt_count": missing_count,
                "missing_alt_sources": missing_alt[:5],
                "lazy_loaded_count": lazy_count,
                "next_gen_count": webp_count,
            },
            "fixable": True,
            "recommendation": "Add descriptive alt tags to all images, enable lazy-loading, and convert images to WebP format.",
        }

    # 7. Internal Links Check
    def check_internal_links(self) -> dict:
        links = self.soup.find_all("a", href=True)
        internal_links = []
        
        for link in links:
            href = link["href"].strip()
            anchor = link.get_text().strip()
            if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            
            if not self.parsed_url or href.startswith("/") or self.parsed_url.netloc in href:
                internal_links.append({"href": href, "anchor": anchor})

        total_int = len(internal_links)
        is_orphan = (self.target_url in self.sitemap_urls) if self.sitemap_urls else False

        status = "pass"
        score = 100
        issues = []

        if total_int == 0:
            status = "warn"
            score -= 30
            issues.append("No internal links found on page.")
        elif total_int < 3:
            status = "warn"
            score -= 15
            issues.append(f"Only {total_int} internal links found (recommended: 3+).")

        if is_orphan:
            status = "fail"
            score -= 40
            issues.append("Orphan page detected: URL not found in sitemap.xml structure.")

        msg = f"Found {total_int} internal links."
        if issues:
            msg += " " + " ".join(issues)

        return {
            "id": "internal_links",
            "category": "Linking",
            "name": "Internal Links & Orphan Detection",
            "status": status,
            "score": max(0, score),
            "message": msg,
            "details": {"internal_links_count": total_int, "sample_links": internal_links[:5]},
            "fixable": True,
            "recommendation": "Add contextual internal links to key site pages using descriptive anchor text.",
        }

    # 8. External Links Check
    def check_external_links(self) -> dict:
        links = self.soup.find_all("a", href=True)
        external_links = []

        for link in links:
            href = link["href"].strip()
            rel = link.get("rel", "")
            if isinstance(rel, list):
                rel = " ".join(rel)
            
            if self.parsed_url and href.startswith("http") and self.parsed_url.netloc not in href:
                external_links.append({"href": href, "nofollow": "nofollow" in rel.lower()})

        total_ext = len(external_links)
        dofollow_count = sum(1 for l in external_links if not l["nofollow"])
        nofollow_count = total_ext - dofollow_count

        status = "pass"
        score = 100
        issues = []

        if total_ext == 0:
            score -= 10
            issues.append("No outbound external links found.")

        msg = f"Found {total_ext} external links ({dofollow_count} dofollow, {nofollow_count} nofollow)."
        if issues:
            msg += " " + " ".join(issues)

        return {
            "id": "external_links",
            "category": "Linking",
            "name": "External Links & Rel Attributes",
            "status": status,
            "score": max(0, score),
            "message": msg,
            "details": {
                "external_links_count": total_ext,
                "dofollow_count": dofollow_count,
                "nofollow_count": nofollow_count,
            },
            "fixable": False,
            "recommendation": "Include authoritative external citations with proper rel='nofollow' attributes where applicable.",
        }

    # 9. Technical SEO & Schema Check
    def check_technical(self) -> dict:
        status = "pass"
        score = 100
        issues = []

        # Canonical
        canonical_tag = self.soup.find("link", attrs={"rel": re.compile(r"^canonical$", re.I)})
        has_canonical = bool(canonical_tag and canonical_tag.get("href"))

        if not has_canonical:
            status = "warn"
            score -= 20
            issues.append("Missing rel='canonical' tag.")

        # Meta Robots
        meta_robots = self.soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
        robots_content = meta_robots.get("content", "").lower() if meta_robots else ""
        is_noindex = "noindex" in robots_content

        if is_noindex:
            status = "fail"
            score -= 50
            issues.append("CRITICAL: Meta robots contains 'noindex', preventing search engine indexing!")

        # Mobile Viewport
        viewport = self.soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
        has_viewport = bool(viewport)

        if not has_viewport:
            status = "fail" if status != "fail" else status
            score -= 25
            issues.append("Missing mobile viewport meta tag ('<meta name=\"viewport\"...>')")

        # Schema.org JSON-LD
        schemas = self.soup.find_all("script", attrs={"type": "application/ld+json"})
        has_schema = len(schemas) > 0
        schema_types = []
        for s in schemas:
            if s.string and "@type" in s.string:
                match = re.search(r'"@type"\s*:\s*"([^"]+)"', s.string)
                if match:
                    schema_types.append(match.group(1))

        if not has_schema:
            status = "warn" if status == "pass" else status
            score -= 15
            issues.append("No Schema.org JSON-LD structured data detected.")

        # HTTPS
        is_https = self.target_url.startswith("https://") if self.parsed_url else True
        if not is_https:
            score -= 20
            issues.append("Page is not using secure HTTPS protocol.")

        msg = f"Technical checks completed. Canonical: {'Yes' if has_canonical else 'No'}, Schema: {', '.join(schema_types) if schema_types else 'None'}."
        if issues:
            msg += " " + " ".join(issues)

        return {
            "id": "technical_seo",
            "category": "Technical",
            "name": "Technical SEO, Schema & Viewport",
            "status": status,
            "score": max(0, score),
            "message": msg,
            "details": {
                "has_canonical": has_canonical,
                "is_noindex": is_noindex,
                "has_viewport": has_viewport,
                "has_schema": has_schema,
                "schema_types": schema_types,
                "is_https": is_https,
            },
            "fixable": True,
            "recommendation": "Ensure canonical link, mobile viewport tag, and JSON-LD schema (Article/Product/FAQ) are present.",
        }
