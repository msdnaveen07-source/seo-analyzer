from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import json

from backend.db.database import get_db, Base, engine
from backend.db.models import AuditLog, KeywordCache
from backend.agent.orchestrator import SEOAgentOrchestrator
from backend.agent.fix_engine import AutonomousFixEngine

# Create DB tables if not created
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api", tags=["audit"])
orchestrator = SEOAgentOrchestrator()
fix_engine = AutonomousFixEngine()

class AuditRequest(BaseModel):
    target: str
    keyword: Optional[str] = ""

class FixRequest(BaseModel):
    file_path: Optional[str] = None
    check_id: str
    keyword: Optional[str] = ""

@router.post("/audit")
def run_audit(req: AuditRequest, db: Session = Depends(get_db)):
    if not req.target.strip():
        raise HTTPException(status_code=400, detail="Target URL or file path is required.")
    
    res = orchestrator.run_full_audit(req.target.strip(), req.keyword.strip(), db=db)
    if not res.get("success"):
        raise HTTPException(status_code=500, detail=res.get("error", "Audit execution failed."))
    return res

@router.get("/audit/{audit_id}")
def get_audit(audit_id: int, db: Session = Depends(get_db)):
    log = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found.")
    return log

@router.get("/history")
def get_history(target: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AuditLog)
    if target:
        query = query.filter(AuditLog.target == target)
    logs = query.order_by(AuditLog.created_at.asc()).all()
    
    history_data = []
    for log in logs:
        history_data.append({
            "id": log.id,
            "target": log.target,
            "score": log.overall_score,
            "category_scores": log.category_scores,
            "timestamp": log.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    return history_data

@router.post("/fix")
def apply_fix(req: FixRequest):
    if req.file_path:
        res = fix_engine.apply_fix_in_place(req.file_path, req.check_id, req.keyword)
        if not res.get("success"):
            raise HTTPException(status_code=400, detail=res.get("error", "Failed to apply fix in-place."))
        return res
    else:
        fix = fix_engine.generate_fix(req.check_id, {}, req.keyword)
        return {"success": True, "fix_details": fix}

@router.get("/export/markdown/{audit_id}")
def export_markdown(audit_id: int, db: Session = Depends(get_db)):
    log = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found.")

    md = f"""# On-Page SEO Audit Report

**Target:** `{log.target}`  
**Target Keyword:** `{log.target_keyword or 'N/A'}`  
**Page Type:** `{log.page_type.upper()}`  
**Audit Date:** {log.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}  

---

## Overall Score: {log.overall_score} / 100

### Category Score Breakdown
"""
    for cat, score in (log.category_scores or {}).items():
        md += f"- **{cat}:** {score} / 100\n"

    md += f"\n### Agent Planner Summary\n> {log.planner_summary}\n\n"
    md += "--- \n\n## Audit Checks Detail\n\n"

    for chk in (log.checks_result or []):
        icon = "✅ PASS" if chk['status'] == 'pass' else ("⚠️ WARN" if chk['status'] == 'warn' else "❌ FAIL")
        md += f"### {icon}: {chk['name']}\n"
        md += f"- **Category:** {chk['category']}\n"
        md += f"- **Score:** {chk['score']} / 100\n"
        md += f"- **Message:** {chk['message']}\n"
        if chk.get('recommendation'):
            md += f"- **Recommendation:** {chk['recommendation']}\n"
        md += "\n"

    return Response(content=md, media_type="text/markdown", headers={
        "Content-Disposition": f"attachment; filename=seo_audit_{audit_id}.md"
    })
