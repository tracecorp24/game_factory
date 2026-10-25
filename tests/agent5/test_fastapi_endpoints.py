"""
Integration tests for FastAPI REST API endpoints using httpx AsyncClient.
Validates acceptance criteria: OpenAPI Swagger /docs documentation completeness and endpoint functionality.
CreativeForge Intelligence Studio v3.0 - Section J.
"""

import httpx
import pytest
from services.api.app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_health_check():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["version"] == "3.0.0"


@pytest.mark.asyncio
async def test_openapi_docs_completeness():
    """
    CRITICAL ACCEPTANCE CRITERION:
    FastAPI OpenAPI documentation (/docs, /openapi.json) must expose all endpoints cleanly.
    """
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/openapi.json")
        assert res.status_code == 200
        openapi = res.json()
        paths = openapi.get("paths", {})

        # Verify key Section J endpoint presence
        required_endpoints = [
            "/api/v1/projects",
            "/api/v1/trends/sources",
            "/api/v1/trends/sync",
            "/api/v1/games/{game_id}/versions",
            "/api/v1/projects/{project_id}/concepts/generate",
            "/api/v1/concepts/{concept_id}/decision",
            "/api/v1/workflows",
            "/api/v1/workflows/{workflow_id}/runs",
            "/api/v1/runs/{run_id}/pause",
            "/api/v1/runs/{run_id}/resume",
            "/api/v1/runs/{run_id}/cancel",
            "/api/v1/runs/{run_id}/events",
            "/api/v1/runs/{run_id}/events/stream",
            "/api/v1/runs/{run_id}/model-calls",
            "/api/v1/runs/{run_id}/attempts",
            "/api/v1/artifacts/{artifact_id}/evaluate",
            "/api/v1/artifacts/{artifact_id}/review",
            "/api/v1/quality/gates",
            "/api/v1/experiments",
            "/api/v1/analytics/overview",
            "/api/v1/analytics/costs",
            "/api/v1/analytics/agents",
            "/api/v1/analytics/export",
            "/api/v1/runs/compare",
            "/api/v1/model-policies",
            "/api/v1/retention",
            "/api/v1/audit",
        ]

        for ep in required_endpoints:
            assert ep in paths, f"Expected endpoint '{ep}' missing from OpenAPI specification!"


@pytest.mark.asyncio
async def test_projects_crud():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        create_res = await client.post(
            "/api/v1/projects",
            json={"name": "Test Match3 Campaign", "workspace_id": "ws_test"},
        )
        assert create_res.status_code == 201
        project = create_res.json()
        pid = project["id"]

        get_res = await client.get(f"/api/v1/projects/{pid}")
        assert get_res.status_code == 200
        assert get_res.json()["name"] == "Test Match3 Campaign"


@pytest.mark.asyncio
async def test_artifact_evaluation_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "artifact_id": "art_api_test_01",
            "run_id": "run_api_test",
            "target_type": "image",
            "media_meta": {
                "width": 1080,
                "height": 1920,
                "format": "png",
                "cta_text": "Play Now",
                "contrast_ratio": 5.2,
                "sha256": "d" * 64,
                "bytes": 204800,
            },
            "creative_hypothesis": {
                "intended_hook": "Tap the matching gems!",
                "creative_mechanism": "Match-3 chain blast",
            },
        }

        eval_res = await client.post("/api/v1/artifacts/art_api_test_01/evaluate", json=payload)
        assert eval_res.status_code == 200
        report = eval_res.json()
        assert report["overall_verdict"] == "PASSED"
        assert report["overall_score"] >= 3.0
        assert len(report["gate_results"]) == 7


@pytest.mark.asyncio
async def test_human_review_and_quality_gates():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Check gate definitions
        gates_res = await client.get("/api/v1/quality/gates")
        assert gates_res.status_code == 200
        gates_data = gates_res.json()
        assert len(gates_data["gates"]) == 7

        # Review submission
        rev_res = await client.post(
            "/api/v1/artifacts/art_api_test_01/review",
            json={
                "artifact_id": "art_api_test_01",
                "reviewer_id": "usr_qa_lead",
                "decision": "approved",
                "reason": "Perfect framing and crisp CTA readability.",
            },
        )
        assert rev_res.status_code == 200
        assert rev_res.json()["decision"] == "approved"


@pytest.mark.asyncio
async def test_analytics_endpoints_and_export():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Overview
        overview_res = await client.get("/api/v1/analytics/overview")
        assert overview_res.status_code == 200
        overview = overview_res.json()
        assert "total_runs" in overview

        # Costs
        costs_res = await client.get("/api/v1/analytics/costs")
        assert costs_res.status_code == 200
        costs = costs_res.json()
        assert "total_billable_tokens" in costs

        # CSV Export
        export_csv = await client.get("/api/v1/analytics/export?format=csv")
        assert export_csv.status_code == 200
        assert export_csv.headers["content-type"].startswith("text/csv")
        assert "total_runs" in export_csv.text

        # JSONL Export
        export_jsonl = await client.get("/api/v1/analytics/export?format=jsonl")
        assert export_jsonl.status_code == 200
        assert "application/x-ndjson" in export_jsonl.headers["content-type"]
