"""API tests: health, analyze, upload, history, model-info, analytics."""

from __future__ import annotations


class TestHealth:
    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["data"]["status"] == "ok"


class TestAnalyze:
    def test_analyze_spam(self, client, sample_spam):
        r = client.post("/api/analyze", json=sample_spam)
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["classification"] in ("SPAM", "POSSIBLE PHISHING")
        assert 0 <= data["risk_score"] <= 100
        assert "risk_level" in data
        assert "confidence" in data
        assert isinstance(data["threat_indicators"], list)
        assert isinstance(data["statistics"], dict)
        # AI is mocked in tests -> should be available.
        assert data["ai_analysis"]["available"] is True

    def test_analyze_safe(self, client, sample_safe):
        r = client.post("/api/analyze", json=sample_safe)
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["classification"] == "SAFE"

    def test_analyze_empty_returns_validation_error(self, client):
        r = client.post("/api/analyze", json={"subject": "", "sender": "", "body": ""})
        assert r.status_code == 422
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] in ("empty_email", "validation_error")


class TestHistory:
    def test_history_lifecycle(self, client, sample_spam):
        created = client.post("/api/analyze", json=sample_spam).json()["data"]
        scan_id = created["_id"]

        # List
        r = client.get("/api/history")
        assert r.status_code == 200
        assert r.json()["data"]["total"] >= 1

        # Get by id
        r = client.get(f"/api/history/{scan_id}")
        assert r.status_code == 200
        assert r.json()["data"]["_id"] == scan_id

        # Report (PDF)
        r = client.get(f"/api/history/{scan_id}/report")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content[:4] == b"%PDF"

        # Delete
        r = client.delete(f"/api/history/{scan_id}")
        assert r.status_code == 200
        assert r.json()["data"]["deleted"] is True

        # Get after delete -> 404
        r = client.get(f"/api/history/{scan_id}")
        assert r.status_code == 404


class TestModelInfo:
    def test_model_info(self, client):
        r = client.get("/api/model-info")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["loaded"] is True
        assert data["model_name"]
        assert data["metrics"]["models"]


class TestAnalytics:
    def test_analytics(self, client):
        r = client.get("/api/analytics")
        assert r.status_code == 200
        data = r.json()["data"]
        assert "total_scans" in data
        assert "classification_counts" in data
