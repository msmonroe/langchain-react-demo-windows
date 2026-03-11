from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app as backend_app


@pytest.fixture(autouse=True)
def _reset_metrics():
    backend_app.metrics.reset()
    yield
    backend_app.metrics.reset()


@pytest.fixture
def client():
    return TestClient(backend_app.app)


def test_health_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"


def test_ask_requires_question(client):
    res = client.post("/ask", json={"question": ""})
    assert res.status_code == 400
    snapshot = backend_app.metrics.snapshot()
    assert snapshot["total_requests"] == 1
    assert snapshot["total_failures"] == 1


def test_ask_returns_answer_and_records_metrics(client, monkeypatch):
    monkeypatch.setattr(backend_app, "ask_question", lambda q: "mocked" if q == "Hello" else "unexpected")

    res = client.post("/ask", json={"question": "Hello"})
    assert res.status_code == 200
    body = res.json()
    assert body["answer"] == "mocked"
    assert "latency_ms" in body
    snapshot = backend_app.metrics.snapshot()
    assert snapshot["total_requests"] == 1
    assert snapshot["total_failures"] == 0
    assert snapshot["avg_latency_ms"] >= 0


def test_ask_handles_pipeline_errors(client, monkeypatch):
    def _boom(_):
        raise RuntimeError("boom")

    monkeypatch.setattr(backend_app, "ask_question", _boom)

    res = client.post("/ask", json={"question": "Hello"})
    assert res.status_code == 500
    snapshot = backend_app.metrics.snapshot()
    assert snapshot["total_requests"] == 1
    assert snapshot["total_failures"] == 1


def test_metrics_endpoint_reports_snapshot(client, monkeypatch):
    monkeypatch.setattr(backend_app, "ask_question", lambda _: "ok")
    client.post("/ask", json={"question": "ping"})

    res = client.get("/metrics")
    assert res.status_code == 200
    snapshot = res.json()
    assert set(snapshot.keys()) == {"total_requests", "total_failures", "avg_latency_ms", "success_rate"}
