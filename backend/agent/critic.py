import json
import re

class SelfCritiqueEngine:
    """
    Autonomously evaluates fix recommendations and generated HTML snippets
    against strict SEO standards before output or in-place file editing.
    """
    def critique_title_fix(self, suggested_title: str, keyword: str) -> dict:
        length = len(suggested_title)
        has_kw = (keyword.lower() in suggested_title.lower()) if keyword else True
        kw_start = (suggested_title.lower().find(keyword.lower()) <= 20) if (keyword and has_kw) else True

        valid = (50 <= length <= 60) and has_kw and kw_start
        feedback = []

        if length < 50:
            feedback.append(f"Title is slightly short ({length}/50-60 chars). Add primary brand or secondary keyword modifier.")
        elif length > 60:
            feedback.append(f"Title exceeds 60 chars ({length} chars). Truncate to prevent SERP snippet clipping.")
        
        if not has_kw and keyword:
            feedback.append(f"Title missing primary keyword '{keyword}'.")

        return {
            "valid": valid,
            "title": suggested_title,
            "length": length,
            "feedback": feedback,
        }

    def critique_meta_description_fix(self, suggested_meta: str, keyword: str) -> dict:
        length = len(suggested_meta)
        has_kw = (keyword.lower() in suggested_meta.lower()) if keyword else True
        cta_words = ["learn", "get", "discover", "try", "buy", "find out", "explore", "start", "read", "contact"]
        has_cta = any(w in suggested_meta.lower() for w in cta_words)

        valid = (145 <= length <= 165) and has_kw and has_cta
        feedback = []

        if length < 145 or length > 165:
            feedback.append(f"Meta description length is {length} chars (target: 150-160).")

        if not has_kw and keyword:
            feedback.append(f"Meta description missing target keyword '{keyword}'.")

        if not has_cta:
            feedback.append("Meta description lacks a clear action verb/CTA.")

        return {
            "valid": valid,
            "meta_description": suggested_meta,
            "length": length,
            "feedback": feedback,
        }

    def critique_schema_jsonld(self, jsonld_str: str) -> dict:
        try:
            parsed = json.loads(jsonld_str)
            has_context = parsed.get("@context") == "https://schema.org"
            has_type = "@type" in parsed
            return {
                "valid": has_context and has_type,
                "type": parsed.get("@type", "Unknown"),
                "feedback": [] if (has_context and has_type) else ["Invalid Schema.org structure."],
            }
        except Exception as e:
            return {"valid": False, "type": None, "feedback": [f"JSON-LD parse error: {str(e)}"]}
