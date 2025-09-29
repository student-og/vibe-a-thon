"""API tests for the Generic vs. Branded Medicine Finder."""
from __future__ import annotations

import json
from typing import Generator

import pytest

from app import create_app


@pytest.fixture
def client() -> Generator:
    app = create_app()
    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client


def test_search_requires_minimum_query_length(client) -> None:
    response = client.get("/api/medicines?q=a")
    assert response.status_code == 400
    payload = json.loads(response.data)
    assert "error" in payload


def test_search_returns_results_for_known_brand(client) -> None:
    response = client.get("/api/medicines?q=tylenol")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert payload["count"] >= 1
    assert any(result["generic_name"] == "Acetaminophen" for result in payload["results"])


def test_get_medicine_by_brand(client) -> None:
    response = client.get("/api/medicines/Tylenol")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert payload["brand_name"] == "Tylenol"
    assert payload["generic_name"] == "Acetaminophen"


def test_get_medicine_by_brand_handles_unknown_brand(client) -> None:
    response = client.get("/api/medicines/UnknownBrand")
    assert response.status_code == 404
    payload = json.loads(response.data)
    assert "error" in payload
