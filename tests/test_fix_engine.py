import os
import tempfile
from backend.agent.fix_engine import AutonomousFixEngine

def test_apply_fix_in_place():
    fix_engine = AutonomousFixEngine()
    
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write("<html><head></head><body><h1>Old Title</h1></body></html>")
        tmp_path = tmp.name

    try:
        res = fix_engine.apply_fix_in_place(tmp_path, "title_tag", "Local SEO Guide")
        assert res["success"] is True
        assert os.path.exists(res["backup_path"])
        
        with open(tmp_path, "r", encoding="utf-8") as f:
            updated_content = f.read()
        assert "<title>" in updated_content
        assert "Local SEO Guide" in updated_content
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
