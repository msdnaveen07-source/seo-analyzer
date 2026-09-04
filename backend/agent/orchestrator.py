from sqlalchemy.orm import Session
from backend.tools.crawler import DocumentFetcher
from backend.tools.seo_checks import SEOChecker
from backend.tools.keyword_research import KeywordResearcher
from backend.tools.lighthouse_runner import LighthouseRunner
from backend.agent.planner import AgentPlanner
from backend.agent.fix_engine import AutonomousFixEngine
from backend.agent.backlink_engine import AutonomousBacklinkEngine
from backend.db.models import AuditLog, KeywordCache
import os

class SEOAgentOrchestrator:
    def __init__(self):
        self.fetcher = DocumentFetcher()
        self.planner = AgentPlanner()
        self.kw_researcher = KeywordResearcher()
        self.lh_runner = LighthouseRunner()
        self.fix_engine = AutonomousFixEngine()
        self.backlink_engine = AutonomousBacklinkEngine()

    def run_full_audit(self, target: str, keyword: str = "", db: Session = None) -> dict:
        """
        Executes full agentic audit workflow:
        1. Fetch HTML / read file
        2. Sitemap & Robots discovery
        3. Agent Planner page classification & weighting
        4. Run modular SEO checks
        5. Keyword Research (Autosuggest, Pytrends, SERP)
        6. Performance & Core Web Vitals audit
        7. Autonomous Backlink Generation & Link Report
        8. Calculate category scores & overall weighted score
        9. Generate fix recommendations with self-critique loop
        10. Save history log to SQLite database
        """
        # 1. Fetch document
        doc = self.fetcher.fetch(target)
        if not doc["success"]:
            return {"success": False, "error": doc.get("error", "Failed to fetch document.")}

        html = doc["html"]
        is_local = doc["is_local"]

        # 2. Robots & Sitemap
        robots = self.fetcher.fetch_robots_txt(target) if not is_local else {"exists": False, "content": ""}
        sitemap = self.fetcher.fetch_sitemap(target) if not is_local else {"exists": False, "urls": []}

        # 3. Agent Planner
        plan = self.planner.plan(html, target, keyword)

        # 4. Modular SEO checks
        checker = SEOChecker(html, target, keyword, sitemap.get("urls", []))
        check_results = checker.run_all_checks()

        # 5. Keyword research
        kw_data = {}
        if keyword:
            kw_data = self.kw_researcher.analyze_keyword(keyword)
            # Cache keyword data in DB if session available
            if db:
                try:
                    cache_item = db.query(KeywordCache).filter(KeywordCache.keyword == keyword).first()
                    if not cache_item:
                        cache_item = KeywordCache(
                            keyword=keyword,
                            trends_data={"trend": kw_data.get("trend_data", [])},
                            suggestions=kw_data.get("autosuggest", []),
                            paa_questions=kw_data.get("paa_questions", []),
                            related_searches=kw_data.get("related_searches", []),
                            difficulty_proxy=kw_data.get("difficulty_proxy", 50.0)
                        )
                        db.add(cache_item)
                        db.commit()
                except Exception as e:
                    print(f"Keyword DB cache error: {e}")

        # 6. Performance audit (Lighthouse)
        lh_results = self.lh_runner.run_audit(target)

        # 7. Backlink Engine
        backlink_data = self.backlink_engine.generate_backlinks(target, keyword)

        # 8. Category scoring & overall weighted calculation
        category_map = {}
        for chk in check_results:
            cat = chk["category"]
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(chk["score"])

        category_scores = {cat: round(sum(scores) / len(scores), 1) for cat, scores in category_map.items()}
        category_scores["Performance"] = lh_results.get("performance", 85)

        total_weight = sum(plan["weights"].values()) + 15
        weighted_sum = sum(category_scores.get(cat, 80) * (weight / total_weight) for cat, weight in plan["weights"].items())
        weighted_sum += category_scores.get("Performance", 85) * (15 / total_weight)
        overall_score = round(min(100.0, max(0.0, weighted_sum)), 1)

        # 9. Enrich failed/warning checks with self-critiqued fix recommendations
        for chk in check_results:
            if chk["status"] in ("fail", "warn") and chk["fixable"]:
                chk["fix_recommendation"] = self.fix_engine.generate_fix(chk["id"], chk["details"], keyword, html)

        result_payload = {
            "success": True,
            "target": target,
            "target_type": "file" if is_local else "url",
            "keyword": keyword,
            "page_type": plan["page_type"],
            "planner_summary": plan["summary"],
            "overall_score": overall_score,
            "category_scores": category_scores,
            "checks": check_results,
            "lighthouse": lh_results,
            "keyword_research": kw_data,
            "robots_txt": robots,
            "sitemap": sitemap,
            "backlinks": backlink_data,
        }

        # 9. Store in SQLite DB
        if db:
            try:
                audit_record = AuditLog(
                    target=target,
                    target_type="file" if is_local else "url",
                    target_keyword=keyword,
                    page_type=plan["page_type"],
                    overall_score=overall_score,
                    category_scores=category_scores,
                    checks_result=check_results,
                    planner_summary=plan["summary"]
                )
                db.add(audit_record)
                db.commit()
                db.refresh(audit_record)
                result_payload["audit_id"] = audit_record.id
            except Exception as db_err:
                print(f"Audit log save error: {db_err}")

        return result_payload
