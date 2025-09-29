"""HTTP endpoints for the Generic vs. Branded Medicine Finder."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

from .services.matching import MedicineMatcher

matcher = MedicineMatcher()


def _format_result(raw: Dict[str, Any]) -> Dict[str, Any]:
    brand_price = raw.get("average_brand_price")
    generic_price = raw.get("average_generic_price")
    savings = None
    if isinstance(brand_price, (int, float)) and isinstance(generic_price, (int, float)):
        savings = round(brand_price - generic_price, 2)

    return {
        "brand_name": raw.get("brand_name"),
        "generic_name": raw.get("generic_name"),
        "form": raw.get("form"),
        "strength": raw.get("strength"),
        "indications": raw.get("indications", []),
        "average_brand_price": brand_price,
        "average_generic_price": generic_price,
        "savings": savings,
        "notes": raw.get("notes"),
        "sources": raw.get("sources", []),
    }


def register_routes(app: Flask) -> None:
    """Register HTTP routes on the provided Flask application."""

    @app.get("/")
    def index() -> str:
        """Render the landing page."""
        stats = matcher.get_summary_stats()
        return render_template("index.html", stats=stats)

    @app.get("/api/medicines")
    def search_medicines() -> Any:
        """Search for branded or generic medicines."""
        query = request.args.get("q", "").strip()
        if len(query) < 2:
            return (
                jsonify(
                    {
                        "error": "Please provide at least two characters to search.",
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            results: List[Dict[str, Any]] = [_format_result(item) for item in matcher.search(query)]
        except ValueError as exc:  # pragma: no cover - defensive, should not occur in normal usage
            return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

        return jsonify({"results": results, "count": len(results)})

    @app.get("/api/medicines/<string:brand_name>")
    def get_medicine(brand_name: str) -> Any:
        """Return details for an exact branded medicine match."""
        result = matcher.find_by_brand(brand_name)
        if not result:
            return (
                jsonify({"error": f"No medicine found for brand '{brand_name}'."}),
                HTTPStatus.NOT_FOUND,
            )
        return jsonify(_format_result(result))
