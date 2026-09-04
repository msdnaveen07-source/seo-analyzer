import os
import shutil
import json
import difflib
from datetime import datetime
from bs4 import BeautifulSoup
from backend.agent.critic import SelfCritiqueEngine
from backend.config import BACKUP_DIR

class AutonomousFixEngine:
    def __init__(self):
        self.critic = SelfCritiqueEngine()

    def generate_fix(self, check_id: str, check_details: dict, keyword: str, current_html: str = "") -> dict:
        """
        Generates optimized fix code snippet for a specific failed check.
        Applies self-critique loop to ensure high quality output.
        """
        kw = keyword or "SEO Target"
        kw_title_case = kw.title()

        if check_id == "title_tag":
            # Target 50-60 chars
            base_title = f"{kw_title_case} - Complete Expert Guide & Tips"
            if len(base_title) < 50:
                base_title = f"{kw_title_case}: Complete Expert Guide & Strategies (2026)"
            if len(base_title) > 60:
                base_title = base_title[:57] + "..."

            critique = self.critic.critique_title_fix(base_title, keyword)
            return {
                "check_id": check_id,
                "type": "title",
                "suggested_code": f"<title>{base_title}</title>",
                "replacement_value": base_title,
                "critique": critique,
            }

        elif check_id == "meta_description":
            base_meta = f"Discover everything about {kw}. Read our comprehensive 2026 expert guide to get actionable insights, proven tips, and best results. Learn more today!"
            if len(base_meta) > 160:
                base_meta = base_meta[:157] + "..."
            
            critique = self.critic.critique_meta_description_fix(base_meta, keyword)
            return {
                "check_id": check_id,
                "type": "meta_description",
                "suggested_code": f'<meta name="description" content="{base_meta}">',
                "replacement_value": base_meta,
                "critique": critique,
            }

        elif check_id == "headings_structure":
            h1_code = f"<h1>{kw_title_case}: Ultimate Guide</h1>"
            return {
                "check_id": check_id,
                "type": "h1",
                "suggested_code": h1_code,
                "replacement_value": f"{kw_title_case}: Ultimate Guide",
                "critique": {"valid": True, "feedback": []},
            }

        elif check_id == "images_check":
            img_snippet = f'<!-- Add alt attribute to images -->\n<img src="example.jpg" alt="{kw_title_case} illustration" loading="lazy" />'
            return {
                "check_id": check_id,
                "type": "image_alt",
                "suggested_code": img_snippet,
                "replacement_value": f"{kw_title_case} illustration",
                "critique": {"valid": True, "feedback": []},
            }

        elif check_id == "technical_seo":
            canonical_code = f'<link rel="canonical" href="https://example.com/canonical-page" />\n<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
            schema_data = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": f"{kw_title_case} Guide",
                "author": {"@type": "Organization", "name": "Local SEO Agent"},
            }
            schema_json = json.dumps(schema_data, indent=2)
            schema_code = f'<script type="application/ld+json">\n{schema_json}\n</script>'
            
            return {
                "check_id": check_id,
                "type": "technical",
                "suggested_code": f"{canonical_code}\n{schema_code}",
                "replacement_value": schema_data,
                "critique": self.critic.critique_schema_jsonld(schema_json),
            }

        return {
            "check_id": check_id,
            "type": "general",
            "suggested_code": f"<!-- General recommendation for {check_id} with keyword '{keyword}' -->",
            "replacement_value": "",
            "critique": {"valid": True, "feedback": []},
        }

    def apply_fix_in_place(self, file_path: str, check_id: str, keyword: str) -> dict:
        """
        Autonomous mode: directly modifies local HTML file in-place after creating a backup.
        Generates unified diff between original and updated HTML.
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File '{file_path}' does not exist."}

        # 1. Create backup copy
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_filename = f"{filename}.{timestamp}.bak"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        shutil.copy2(file_path, backup_path)

        # 2. Read original HTML
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            original_html = f.read()

        soup = BeautifulSoup(original_html, "html.parser")
        fix_info = self.generate_fix(check_id, {}, keyword, original_html)
        replacement = fix_info["replacement_value"]

        # 3. Apply DOM modifications based on check_id
        if check_id == "title_tag":
            title_tag = soup.find("title")
            if title_tag:
                title_tag.string = replacement
            else:
                head = soup.find("head") or soup
                new_title = soup.new_tag("title")
                new_title.string = replacement
                head.append(new_title)

        elif check_id == "meta_description":
            meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
            if meta_desc:
                meta_desc["content"] = replacement
            else:
                head = soup.find("head") or soup
                new_meta = soup.new_tag("meta", attrs={"name": "description", "content": replacement})
                head.append(new_meta)

        elif check_id == "headings_structure":
            h1s = soup.find_all("h1")
            if h1s:
                h1s[0].string = replacement
            else:
                body = soup.find("body") or soup
                new_h1 = soup.new_tag("h1")
                new_h1.string = replacement
                body.insert(0, new_h1)

        elif check_id == "images_check":
            imgs = soup.find_all("img")
            for img in imgs:
                if not img.get("alt"):
                    img["alt"] = replacement
                if not img.get("loading"):
                    img["loading"] = "lazy"

        elif check_id == "technical_seo":
            head = soup.find("head") or soup
            # Canonical
            if not soup.find("link", attrs={"rel": "canonical"}):
                can_tag = soup.new_tag("link", attrs={"rel": "canonical", "href": "https://localhost/canonical-path"})
                head.append(can_tag)
            # Viewport
            if not soup.find("meta", attrs={"name": "viewport"}):
                vp_tag = soup.new_tag("meta", attrs={"name": "viewport", "content": "width=device-width, initial-scale=1.0"})
                head.append(vp_tag)

        updated_html = soup.prettify()

        # 4. Save modified HTML back to file_path
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_html)

        # 5. Generate unified text diff
        diff_lines = list(difflib.unified_diff(
            original_html.splitlines(),
            updated_html.splitlines(),
            fromfile=f"original/{filename}",
            tofile=f"modified/{filename}",
            lineterm=""
        ))
        diff_text = "\n".join(diff_lines[:50]) # cap for clean view

        return {
            "success": True,
            "file_path": file_path,
            "backup_path": backup_path,
            "check_id": check_id,
            "diff": diff_text,
            "before_html": original_html,
            "after_html": updated_html,
            "fix_details": fix_info,
        }
