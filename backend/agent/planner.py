from bs4 import BeautifulSoup

class AgentPlanner:
    """
    Given a URL/file and parsed BeautifulSoup content, determines page context
    (e.g., e-commerce product page, blog post, homepage, landing page)
    and constructs a customized execution & scoring plan.
    """
    def plan(self, html: str, target: str, keyword: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        
        # Detect page type
        page_type = "blog_post"
        if soup.find("form", attrs={"action": lambda x: x and "cart" in x}) or soup.find(class_=lambda x: x and "product" in str(x).lower()):
            page_type = "product_page"
        elif target.rstrip("/").count("/") <= 3 and ("home" in target.lower() or target.endswith((".com", ".org", ".io", ".net"))):
            page_type = "homepage"
        elif soup.find("article") or len(soup.find_all("p")) > 5:
            page_type = "blog_post"

        weights = {
            "title_tag": 20,
            "meta_description": 15,
            "headings_structure": 15,
            "content_readability": 20,
            "images_check": 10,
            "internal_links": 10,
            "technical_seo": 10,
        }

        if page_type == "product_page":
            weights["images_check"] = 15
            weights["technical_seo"] = 15
            weights["content_readability"] = 10
        elif page_type == "homepage":
            weights["technical_seo"] = 20
            weights["title_tag"] = 25

        summary = f"Identified page type: '{page_type.upper()}'. Prioritizing {'Images & Schema' if page_type == 'product_page' else 'Title & Content Depth'}. Adjusted check weightings accordingly."

        return {
            "page_type": page_type,
            "weights": weights,
            "summary": summary,
        }
