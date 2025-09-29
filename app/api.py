"""HTTP endpoints for the Generic vs. Branded Medicine Finder."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request

from .services.matching import MedicineMatcher
from .services.pharmacy_finder import PharmacyFinder

matcher = MedicineMatcher()
pharmacy_finder = PharmacyFinder()


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

    @app.get("/api/pharmacies")
    def find_pharmacies() -> Any:
        """Find nearby pharmacies based on location.
        
        Query params:
        - location: ZIP code, city, or address (required)
        - radius: search radius in miles (default: 5.0)
        - limit: maximum number of results (default: 10)
        - pricing: filter by pricing tier ("low", "medium", "high")
        """
        location = request.args.get("location", "").strip()
        if not location:
            return (
                jsonify({"error": "Location parameter is required."}),
                HTTPStatus.BAD_REQUEST,
            )
        
        try:
            radius = float(request.args.get("radius", 5.0))
            limit = int(request.args.get("limit", 10))
        except ValueError:
            return (
                jsonify({"error": "Invalid radius or limit parameter."}),
                HTTPStatus.BAD_REQUEST,
            )
        
        pricing = request.args.get("pricing", "").strip() or None
        
        try:
            pharmacies = pharmacy_finder.find_nearby_pharmacies(
                location=location,
                radius_miles=radius,
                limit=limit,
                pricing_preference=pricing
            )
            return jsonify({
                "pharmacies": pharmacies,
                "count": len(pharmacies),
                "search_location": location,
                "radius_miles": radius
            })
        except Exception as exc:
            return jsonify({"error": f"Error finding pharmacies: {str(exc)}"}), HTTPStatus.INTERNAL_SERVER_ERROR

    @app.get("/api/pharmacies/<string:name>")
    def get_pharmacy_details(name: str) -> Any:
        """Get detailed information about a specific pharmacy."""
        result = pharmacy_finder.get_pharmacy_details(name)
        if not result:
            return (
                jsonify({"error": f"No pharmacy found with name '{name}'."}),
                HTTPStatus.NOT_FOUND,
            )
        return jsonify(result)

    @app.get("/api/education/<string:topic>")
    def get_educational_content(topic: str) -> Any:
        """Get educational content about medications and healthcare.
        
        Available topics:
        - generic-medicines: Information about generic vs brand medicines
        - chronic-conditions: Managing chronic conditions
        - savings-tips: Tips for saving on prescription costs
        - fda-approval: FDA approval process for generics
        """
        educational_content = {
            "generic-medicines": {
                "title": "Understanding Generic Medicines",
                "sections": [
                    {
                        "heading": "What are Generic Medicines?",
                        "content": "Generic medicines contain the same active ingredients as brand-name drugs and are proven to work just as well. They must meet the same strict FDA standards for quality, strength, purity, and stability."
                    },
                    {
                        "heading": "FDA Requirements",
                        "content": "Generic drugs must demonstrate bioequivalence to the brand-name drug, meaning they work in the body the same way. They must contain identical amounts of the same active ingredient and be manufactured under strict quality standards."
                    },
                    {
                        "heading": "Cost Savings",
                        "content": "Generic medicines typically cost 80-85% less than brand-name drugs because manufacturers don't need to repeat expensive clinical trials or invest in marketing."
                    }
                ],
                "disclaimer": "Always consult your healthcare provider before switching medications."
            },
            "chronic-conditions": {
                "title": "Managing Chronic Conditions",
                "sections": [
                    {
                        "heading": "Diabetes Management",
                        "content": "Generic Metformin can save over $2,000 annually compared to brand-name alternatives while providing identical blood sugar control."
                    },
                    {
                        "heading": "Hypertension Treatment",
                        "content": "Generic ACE inhibitors and beta-blockers offer the same cardiovascular protection as brand names at significantly lower costs."
                    },
                    {
                        "heading": "Cholesterol Management",
                        "content": "Generic statins like Atorvastatin provide identical cholesterol-lowering benefits at a fraction of the cost of brand-name drugs."
                    }
                ],
                "disclaimer": "Never stop or change chronic medications without consulting your healthcare provider."
            },
            "savings-tips": {
                "title": "Prescription Savings Tips",
                "sections": [
                    {
                        "heading": "Generic First",
                        "content": "Always ask your doctor if a generic alternative is available. Generic drugs offer the same therapeutic benefits at much lower costs."
                    },
                    {
                        "heading": "90-Day Supplies",
                        "content": "Purchasing 90-day supplies instead of 30-day supplies often reduces per-dose costs and copays."
                    },
                    {
                        "heading": "Pharmacy Shopping",
                        "content": "Prices can vary significantly between pharmacies. Compare prices at different chains, independents, and online pharmacies."
                    },
                    {
                        "heading": "Discount Programs",
                        "content": "Many pharmacies offer $4 generic programs, membership discounts, and loyalty rewards that can reduce costs."
                    }
                ],
                "disclaimer": "Always verify coverage with your insurance plan before making purchases."
            },
            "fda-approval": {
                "title": "FDA Generic Drug Approval Process",
                "sections": [
                    {
                        "heading": "Bioequivalence Studies",
                        "content": "Generic manufacturers must prove their drug performs identically to the brand-name drug in healthy volunteers through pharmacokinetic studies."
                    },
                    {
                        "heading": "Quality Standards",
                        "content": "Generic drugs are manufactured under the same current Good Manufacturing Practice (cGMP) standards as brand-name drugs, ensuring consistent quality."
                    },
                    {
                        "heading": "FDA Inspection",
                        "content": "All generic drug manufacturing facilities are subject to regular FDA inspections to ensure compliance with safety and quality standards."
                    }
                ],
                "disclaimer": "The FDA's rigorous approval process ensures generic drugs are safe and effective."
            }
        }
        
        content = educational_content.get(topic)
        if not content:
            return (
                jsonify({"error": f"Educational topic '{topic}' not found."}),
                HTTPStatus.NOT_FOUND,
            )
        
        return jsonify(content)

    @app.post("/api/calculate-savings")
    def calculate_annual_savings() -> Any:
        """Calculate annual savings when switching from brand to generic.
        
        Expected JSON payload:
        {
            "brand_price": float,
            "generic_price": float,
            "prescriptions_per_year": int,
            "medicine_name": str (optional)
        }
        """
        if not request.is_json:
            return (
                jsonify({"error": "JSON payload required."}),
                HTTPStatus.BAD_REQUEST,
            )
            
        data = request.get_json()
        if data is None:
            return (
                jsonify({"error": "JSON payload required."}),
                HTTPStatus.BAD_REQUEST,
            )
        
        try:
            brand_price = float(data.get("brand_price", 0))
            generic_price = float(data.get("generic_price", 0))
            prescriptions_per_year = int(data.get("prescriptions_per_year", 12))
        except (ValueError, TypeError):
            return (
                jsonify({"error": "Invalid price or prescription data."}),
                HTTPStatus.BAD_REQUEST,
            )
        
        if brand_price <= 0 or generic_price <= 0 or prescriptions_per_year <= 0:
            return (
                jsonify({"error": "Prices and prescription count must be positive."}),
                HTTPStatus.BAD_REQUEST,
            )
        
        brand_annual = brand_price * prescriptions_per_year
        generic_annual = generic_price * prescriptions_per_year
        annual_savings = brand_annual - generic_annual
        
        percentage_saved = (annual_savings / brand_annual) * 100 if brand_annual > 0 else 0
        
        result = {
            "brand_annual_cost": round(brand_annual, 2),
            "generic_annual_cost": round(generic_annual, 2),
            "annual_savings": round(annual_savings, 2),
            "percentage_saved": round(percentage_saved, 1),
            "prescriptions_per_year": prescriptions_per_year,
            "medicine_name": data.get("medicine_name", ""),
            "disclaimer": "Always consult your healthcare provider before changing medications."
        }
        
        return jsonify(result)
