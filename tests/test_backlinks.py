import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_backlinks_workflow():
    # 1. Post a single backlink
    payload = {
        "target_url": "https://mywebsite.com/seo-guide",
        "submitted_url": "https://medium.com/@user/best-seo-tips-2026",
        "anchor_text": "SEO Guide",
        "link_type": "dofollow",
        "submission_category": "Web 2.0",
        "da_score": 95,
        "notes": "Published blog post on Medium"
    }
    response = client.post("/api/backlinks/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    sub_id = data["id"]

    # 2. Get Backlinks list
    get_res = client.get("/api/backlinks/")
    assert get_res.status_code == 200
    list_data = get_res.json()
    assert list_data["total"] >= 1

    # 3. Get Stats
    stats_res = client.get("/api/backlinks/stats")
    assert stats_res.status_code == 200
    stats_data = stats_res.json()
    assert stats_data["total_links"] >= 1
    assert "daily_goal" in stats_data
    assert stats_data["daily_goal"] == 300

    # 4. Get High DA targets catalog
    targets_res = client.get("/api/backlinks/high-da-targets")
    assert targets_res.status_code == 200
    targets_data = targets_res.json()
    assert len(targets_data["targets"]) >= 20

    # 5. Bulk Add
    bulk_payload = {
        "target_url": "https://mywebsite.com",
        "urls_raw": "https://tumblr.com/post1\nhttps://reddit.com/r/seo/post2",
        "anchor_text": "My Website",
        "link_type": "dofollow",
        "submission_category": "Web 2.0",
        "da_score": 80
    }
    bulk_res = client.post("/api/backlinks/bulk", json=bulk_payload)
    assert bulk_res.status_code == 200
    assert bulk_res.json()["count"] == 2

    # 6. Delete backlink
    del_res = client.delete(f"/api/backlinks/{sub_id}")
    assert del_res.status_code == 200

def test_auto_agent_backlinks():
    payload = {
        "target_url": "https://myauto-site.com",
        "target_keyword": "SEO Automation Guide",
        "count": 5
    }
    res = client.post("/api/backlinks/auto-agent", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["total_created"] == 5

