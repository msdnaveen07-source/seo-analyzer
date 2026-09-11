import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_scrape_markdown_endpoint():
    response = client.post("/api/scrape/markdown", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "markdown" in data
    assert "Example Domain" in data["markdown"] or "example" in data["markdown"].lower()

def test_scrape_extract_endpoint():
    response = client.post("/api/scrape/extract", json={
        "url": "https://example.com",
        "prompt": "Extract headings and title"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data

def test_scrape_monitor_endpoint():
    response = client.post("/api/scrape/monitor", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "content_hash" in data
    assert data["status_code"] == 200
