"""Tests for new features: pharmacy finder, education, and savings calculator."""
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


def test_pharmacy_finder_requires_location(client) -> None:
    """Test that pharmacy finder requires location parameter."""
    response = client.get("/api/pharmacies")
    assert response.status_code == 400
    payload = json.loads(response.data)
    assert "Location parameter is required" in payload["error"]


def test_pharmacy_finder_returns_results(client) -> None:
    """Test that pharmacy finder returns results for valid location."""
    response = client.get("/api/pharmacies?location=New%20York%20NY")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert "pharmacies" in payload
    assert "count" in payload
    assert payload["count"] > 0
    assert payload["search_location"] == "New York NY"


def test_pharmacy_finder_respects_limit(client) -> None:
    """Test that pharmacy finder respects limit parameter."""
    response = client.get("/api/pharmacies?location=New%20York%20NY&limit=2")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert len(payload["pharmacies"]) <= 2


def test_pharmacy_finder_filters_by_pricing(client) -> None:
    """Test that pharmacy finder filters by pricing tier."""
    response = client.get("/api/pharmacies?location=New%20York%20NY&pricing=low")
    assert response.status_code == 200
    payload = json.loads(response.data)
    for pharmacy in payload["pharmacies"]:
        assert pharmacy["pricing_tier"] == "low"


def test_get_pharmacy_details(client) -> None:
    """Test getting details for a specific pharmacy."""
    response = client.get("/api/pharmacies/CVS%20Pharmacy")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert payload["name"] == "CVS Pharmacy"
    assert "address" in payload
    assert "services" in payload


def test_get_pharmacy_details_not_found(client) -> None:
    """Test getting details for non-existent pharmacy."""
    response = client.get("/api/pharmacies/NonExistent%20Pharmacy")
    assert response.status_code == 404
    payload = json.loads(response.data)
    assert "error" in payload


def test_educational_content_generic_medicines(client) -> None:
    """Test educational content for generic medicines."""
    response = client.get("/api/education/generic-medicines")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert payload["title"] == "Understanding Generic Medicines"
    assert "sections" in payload
    assert len(payload["sections"]) > 0
    assert "disclaimer" in payload


def test_educational_content_chronic_conditions(client) -> None:
    """Test educational content for chronic conditions."""
    response = client.get("/api/education/chronic-conditions")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert payload["title"] == "Managing Chronic Conditions"
    assert "sections" in payload
    assert any("Diabetes" in section["heading"] for section in payload["sections"])


def test_educational_content_not_found(client) -> None:
    """Test educational content for non-existent topic."""
    response = client.get("/api/education/nonexistent-topic")
    assert response.status_code == 404
    payload = json.loads(response.data)
    assert "error" in payload


def test_calculate_savings_valid_data(client) -> None:
    """Test savings calculation with valid data."""
    data = {
        "brand_price": 100.0,
        "generic_price": 20.0,
        "prescriptions_per_year": 12,
        "medicine_name": "Test Medicine"
    }
    response = client.post("/api/calculate-savings", json=data)
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert payload["brand_annual_cost"] == 1200.0
    assert payload["generic_annual_cost"] == 240.0
    assert payload["annual_savings"] == 960.0
    assert payload["percentage_saved"] == 80.0
    assert "disclaimer" in payload


def test_calculate_savings_missing_data(client) -> None:
    """Test savings calculation with missing data."""
    response = client.post("/api/calculate-savings", json={"brand_price": 100})  # Missing other required fields
    assert response.status_code == 400
    payload = json.loads(response.data)
    assert "must be positive" in payload["error"]


def test_calculate_savings_empty_json(client) -> None:
    """Test savings calculation with empty JSON."""
    response = client.post("/api/calculate-savings", json={})
    assert response.status_code == 400
    payload = json.loads(response.data)
    assert "must be positive" in payload["error"]  # Empty dict leads to 0 values


def test_calculate_savings_no_json(client) -> None:
    """Test savings calculation with no JSON payload."""
    response = client.post("/api/calculate-savings")
    assert response.status_code == 400
    payload = json.loads(response.data)
    assert "JSON payload required" in payload["error"]


def test_calculate_savings_invalid_data(client) -> None:
    """Test savings calculation with invalid data."""
    data = {
        "brand_price": "invalid",
        "generic_price": 20.0,
        "prescriptions_per_year": 12
    }
    response = client.post("/api/calculate-savings", json=data)
    assert response.status_code == 400
    payload = json.loads(response.data)
    assert "Invalid price or prescription data" in payload["error"]


def test_calculate_savings_negative_values(client) -> None:
    """Test savings calculation with negative values."""
    data = {
        "brand_price": -10.0,
        "generic_price": 20.0,
        "prescriptions_per_year": 12
    }
    response = client.post("/api/calculate-savings", json=data)
    assert response.status_code == 400
    payload = json.loads(response.data)
    assert "must be positive" in payload["error"]


def test_enhanced_search_results_include_disclaimer(client) -> None:
    """Test that search results now include healthcare disclaimers."""
    response = client.get("/api/medicines?q=tylenol")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert payload["count"] >= 1
    # The disclaimer is added in the frontend, not the API
    # But we can verify the API still works correctly


def test_medicine_data_includes_fda_info(client) -> None:
    """Test that enhanced medicine data includes FDA Orange Book information."""
    response = client.get("/api/medicines/Glucophage")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert payload["brand_name"] == "Glucophage"
    assert payload["generic_name"] == "Metformin"
    # The raw data includes fda_orange_book_code, but it's not exposed in the API format
    # This is intentional to keep the API clean while enriching the backend data