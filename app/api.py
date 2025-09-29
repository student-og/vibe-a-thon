"""HTTP endpoints for the Generic vs. Branded Medicine Finder."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request

from .services.matching import MedicineMatcher

matcher = MedicineMatcher()


def _format_result(raw: Dict[str, Any], locality: Optional[str] = None) -> Dict[str, Any]:
    # Optionally localize prices
    if locality:
        raw = matcher.adjust_prices(raw, locality)

    brand_price = raw.get("average_brand_price")
    generic_price = raw.get("average_generic_price")
    savings = None
    if isinstance(brand_price, (int, float)) and isinstance(generic_price, (int, float)):
        savings = round(brand_price - generic_price, 2)

    result = {
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
    if locality:
        # Include transparency about applied adjustment
        result["locality"] = locality
        result["price_adjustment"] = raw.get("price_adjustment")
    return result


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
        locality = request.args.get("locality", "").strip() or None
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
            results: List[Dict[str, Any]] = [_format_result(item, locality) for item in matcher.search(query)]
        except ValueError as exc:  # pragma: no cover - defensive, should not occur in normal usage
            return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR

        return jsonify({"results": results, "count": len(results)})

    @app.get("/api/medicines/<string:name>")
    def get_medicine(name: str) -> Any:
        """Return details for an exact branded or generic medicine match.

        Optional query params:
        - locality: adjust prices for a given locality code
        - include_alternatives: if truthy, include a few alternatives in the payload
        """
        locality = request.args.get("locality", "").strip() or None
        include_alternatives = request.args.get("include_alternatives", "").strip().lower() in {"1", "true", "yes"}

        result = matcher.find_by_brand_or_generic(name)
        if not result:
            return (
                jsonify({"error": f"No medicine found for '{name}'."}),
                HTTPStatus.NOT_FOUND,
            )
        formatted = _format_result(result, locality)

        if include_alternatives:
            alts = matcher.get_alternatives(result)
            if locality:
                alts = [_format_result(item, locality) for item in alts]
            else:
                alts = [_format_result(item) for item in alts]
            formatted["alternatives"] = alts

        return jsonify(formatted)

    @app.get("/api/medicines/<string:name>/alternatives")
    def get_alternatives(name: str) -> Any:
        """Return alternative generic medicines based on shared indications.

        Optional query params:
        - locality: adjust prices for a given locality code
        - limit: maximum number of alternatives to return (default 5)
        """
        base = matcher.find_by_brand_or_generic(name)
        if not base:
            return (
                jsonify({"error": f"No medicine found for '{name}'."}),
                HTTPStatus.NOT_FOUND,
            )
        try:
            limit = int(request.args.get("limit", 5))
        except ValueError:
            limit = 5
        locality = request.args.get("locality", "").strip() or None
        alts = matcher.get_alternatives(base, limit=limit)
        if locality:
            alts = [_format_result(item, locality) for item in alts]
        else:
            alts = [_format_result(item) for item in alts]
        return jsonify({"base": _format_result(base, locality), "alternatives": alts, "count": len(alts)})
