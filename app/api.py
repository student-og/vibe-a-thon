"""HTTP endpoints for the Generic vs. Branded Medicine Finder."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request

from .services.education import EducationLibrary
from .services.i18n import (
    build_metadata as build_i18n_metadata,
    get_all_translations,
    get_supported_languages,
    normalize_language_code,
    translate,
)
from .services.matching import MedicineMatcher
from .services.pharmacy import PharmacyLocator, summarize_offers
from .services.regulatory import RegulatoryDataFetcher, build_refresh_response

matcher = MedicineMatcher()
regulatory_fetcher = RegulatoryDataFetcher()
pharmacy_locator = PharmacyLocator()
education_library = EducationLibrary(matcher)


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


def _resolve_language_from_request() -> str:
    """Return a normalized language code derived from the current request."""
    return normalize_language_code(request.args.get("lang"))


def _advice(lang: str) -> str:
    return translate("advice", lang)


def register_routes(app: Flask) -> None:
    """Register HTTP routes on the provided Flask application."""

    @app.get("/")
    def index() -> str:
        """Render the landing page."""
        lang = _resolve_language_from_request()
        stats = matcher.get_summary_stats()
        return render_template(
            "index.html",
            stats=stats,
            lang=lang,
            supported_languages=list(get_supported_languages()),
        )

    @app.get("/api/medicines")
    def search_medicines() -> Any:
        """Search for branded or generic medicines."""
        query = request.args.get("q", "").strip()
        locality = request.args.get("locality", "").strip() or None
        lang = _resolve_language_from_request()
        if len(query) < 2:
            return (
                jsonify(
                    {
                        "error": translate("ui.feedback.enter_more", lang),
                        "advice": _advice(lang),
                        "language": lang,
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            results: List[Dict[str, Any]] = [_format_result(item, locality) for item in matcher.search(query)]
        except ValueError as exc:  # pragma: no cover - defensive, should not occur in normal usage
            return jsonify({"error": str(exc), "advice": _advice(lang), "language": lang}), HTTPStatus.INTERNAL_SERVER_ERROR

        response_payload: Dict[str, Any] = {
            "results": results,
            "count": len(results),
            "language": lang,
            "advice": _advice(lang),
            "supported_languages": list(get_supported_languages()),
        }
        if results:
            response_payload["summary"] = matcher.get_summary_stats()
            response_payload["locality"] = locality
        return jsonify(response_payload)

    @app.get("/api/medicines/<string:name>")
    def get_medicine(name: str) -> Any:
        """Return details for an exact branded or generic medicine match.

        Optional query params:
        - locality: adjust prices for a given locality code
        - include_alternatives: if truthy, include a few alternatives in the payload
        """
        locality = request.args.get("locality", "").strip() or None
        include_alternatives = request.args.get("include_alternatives", "").strip().lower() in {"1", "true", "yes"}
        lang = _resolve_language_from_request()

        result = matcher.find_by_brand_or_generic(name)
        if not result:
            return (
                jsonify({
                    "error": translate("ui.feedback.none", lang),
                    "query": name,
                    "language": lang,
                    "advice": _advice(lang),
                }),
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

        formatted["language"] = lang
        formatted["advice"] = _advice(lang)

        return jsonify(formatted)

    @app.get("/api/medicines/<string:name>/alternatives")
    def get_alternatives(name: str) -> Any:
        """Return alternative generic medicines based on shared indications.

        Optional query params:
        - locality: adjust prices for a given locality code
        - limit: maximum number of alternatives to return (default 5)
        """
        base = matcher.find_by_brand_or_generic(name)
        lang = _resolve_language_from_request()
        if not base:
            return (
                jsonify({
                    "error": translate("ui.feedback.none", lang),
                    "query": name,
                    "language": lang,
                    "advice": _advice(lang),
                }),
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
        return jsonify(
            {
                "base": _format_result(base, locality),
                "alternatives": alts,
                "count": len(alts),
                "language": lang,
                "advice": _advice(lang),
            }
        )

    @app.get("/api/medicines/<string:name>/pharmacies")
    def get_pharmacies(name: str) -> Any:
        """Surface nearby pharmacy or online offers for a medicine."""
        lang = _resolve_language_from_request()
        locality = request.args.get("locality", "").strip() or None
        try:
            limit = int(request.args.get("limit", 5))
        except ValueError:
            limit = 5
        medicine = matcher.find_by_brand_or_generic(name)
        if not medicine:
            return (
                jsonify({
                    "error": translate("ui.feedback.none", lang),
                    "query": name,
                    "language": lang,
                    "advice": _advice(lang),
                }),
                HTTPStatus.NOT_FOUND,
            )

        offers = pharmacy_locator.find_offers(medicine, locality=locality, limit=limit, lang=lang)
        summary = summarize_offers(offers)
        payload = {
            "offers": offers,
            "summary": summary,
            "medicine": _format_result(medicine, locality),
            "language": lang,
            "advice": _advice(lang),
        }
        if locality:
            payload["locality"] = locality
        return jsonify(payload)

    @app.post("/api/dataset/refresh")
    def refresh_dataset() -> Any:
        """Fetch and merge an enriched dataset from regulatory APIs."""
        lang = _resolve_language_from_request()
        body = request.get_json(silent=True) or {}
        limit = int(body.get("limit", 40))
        offline = body.get("offline")
        offline = True if offline is None else bool(offline)

        dataset, metadata = regulatory_fetcher.fetch_dataset(limit=limit, offline=offline)
        added = matcher.extend_dataset(dataset)
        stats = matcher.get_summary_stats()
        metadata["merged_total"] = matcher.total_medicines
        metadata["offline"] = offline
        metadata["stats_snapshot"] = stats

        response_payload = build_refresh_response(added=added, metadata=metadata, lang=lang)
        response_payload.update({
            "language": lang,
            "stats": stats,
        })
        return jsonify(response_payload)

    @app.get("/api/education/modules")
    def get_education_modules() -> Any:
        """Return educational modules tailored to chronic conditions."""
        lang = _resolve_language_from_request()
        modules = education_library.get_modules(lang)
        return jsonify(
            {
                "modules": modules,
                "count": len(modules),
                "language": lang,
                "advice": _advice(lang),
            }
        )

    @app.post("/api/education/savings")
    def calculate_savings() -> Any:
        """Estimate brand versus generic savings for chronic therapy."""
        lang = _resolve_language_from_request()
        body = request.get_json(silent=True) or {}
        medicine_name = str(body.get("medicine", "")).strip()
        try:
            months = int(body.get("months", 12))
        except (TypeError, ValueError):
            months = 12
        try:
            monthly_quantity = float(body.get("monthly_quantity", 1))
        except (TypeError, ValueError):
            monthly_quantity = 1.0

        try:
            report = education_library.calculate_savings(
                medicine_name,
                months=months,
                monthly_quantity=monthly_quantity,
                lang=lang,
            )
        except ValueError as exc:
            return (
                jsonify({"error": str(exc), "language": lang, "advice": _advice(lang)}),
                HTTPStatus.BAD_REQUEST,
            )

        report["language"] = lang
        return jsonify(report)

    @app.get("/api/i18n")
    def get_i18n() -> Any:
        """Expose translation dictionaries for the front-end."""
        lang = _resolve_language_from_request()
        metadata = build_i18n_metadata(lang)
        metadata["advice"] = _advice(lang)
        return jsonify({"languages": get_all_translations(), "metadata": metadata})
