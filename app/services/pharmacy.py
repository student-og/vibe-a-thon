"""Synthetic pharmacy offer generator with regional pricing adjustments."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Dict, Iterable, List, Optional

from .i18n import translate, normalize_language_code


class PharmacyLocator:
    """Return simulated pharmacy offers for the requested medicine."""

    _CURRENCY_BY_COUNTRY: Dict[str, Dict[str, str]] = {
        "us": {"code": "USD", "symbol": "$"},
        "in": {"code": "INR", "symbol": "₹"},
        "ca": {"code": "CAD", "symbol": "$"},
    }

    _OFFERS: List[Dict[str, object]] = [
        {
            "name": "CityCare Pharmacy",
            "locality": "us-ny",
            "type": "retail",
            "address": "Midtown Manhattan, NY",
            "distance_km": 1.4,
            "price_multiplier": 1.08,
            "delivery_eta": "Same-day courier",
            "url": "https://www.citycarepharmacy.example/offers",
        },
        {
            "name": "Hudson Script",
            "locality": "us-ny",
            "type": "retail",
            "address": "Brooklyn, NY",
            "distance_km": 5.6,
            "price_multiplier": 1.02,
            "delivery_eta": "Pickup in 1 hour",
            "url": "https://www.hudsonscript.example/lookup",
        },
        {
            "name": "CareKart",
            "locality": "online-us",
            "type": "online",
            "address": "Nationwide",
            "distance_km": None,
            "price_multiplier": 0.94,
            "delivery_eta": "2-day shipping",
            "url": "https://www.carekart.example/meds",
        },
        {
            "name": "MediPlus Koramangala",
            "locality": "in-ka",
            "type": "retail",
            "address": "Bengaluru, Karnataka",
            "distance_km": 2.1,
            "price_multiplier": 0.88,
            "delivery_eta": "Bike delivery in 3 hrs",
            "url": "https://www.mediplus.example/offers",
        },
        {
            "name": "PharmaExpress Maharashtra",
            "locality": "in-mh",
            "type": "retail",
            "address": "Mumbai, Maharashtra",
            "distance_km": 4.3,
            "price_multiplier": 0.9,
            "delivery_eta": "Pickup next morning",
            "url": "https://www.pharmaexpress.example/stores",
        },
        {
            "name": "Wellbeing Online",
            "locality": "online-in",
            "type": "online",
            "address": "Pan-India",
            "distance_km": None,
            "price_multiplier": 0.82,
            "delivery_eta": "48-hour courier",
            "url": "https://www.wellbeingonline.example/generics",
        },
    ]

    def find_offers(
        self,
        medicine: Dict[str, object],
        *,
        locality: Optional[str] = None,
        limit: int = 5,
        lang: str | None = None,
    ) -> List[Dict[str, object]]:
        """Return ordered offers for a medicine and locality."""
        if not medicine:
            return []

        normalized_locality = (locality or "").lower()
        matches = [offer for offer in self._OFFERS if self._matches_locality(offer["locality"], normalized_locality)]
        if not matches:
            matches = [offer for offer in self._OFFERS if offer["locality"].startswith("online")]

        currency = self._currency_for_locality(normalized_locality)
        base_price = float(medicine.get("average_generic_price") or medicine.get("average_brand_price") or 0.0)
        if base_price <= 0:
            base_price = 25.0

        offers: List[Dict[str, object]] = []
        now = datetime.now(UTC)
        for offer in matches[:limit]:
            multiplier = float(offer.get("price_multiplier", 1.0))
            price = round(base_price * multiplier, 2)
            offers.append(
                {
                    "partner": offer["name"],
                    "type": offer["type"],
                    "address": offer["address"],
                    "distance_km": offer["distance_km"],
                    "price": price,
                    "currency": currency,
                    "delivery": offer.get("delivery_eta"),
                    "url": offer.get("url"),
                    "last_updated": (now - timedelta(minutes=offer.get("distance_km") or 0))
                    .isoformat(timespec="minutes")
                    .replace("+00:00", "Z"),
                    "advice": translate("advice", normalize_language_code(lang)),
                }
            )
        offers.sort(key=lambda item: item["price"])
        return offers

    def _matches_locality(self, offer_locality: str, requested: str) -> bool:
        if not requested:
            return True
        if offer_locality == requested:
            return True
        offer_country = offer_locality.split("-")[0]
        req_country = requested.split("-")[0]
        return offer_country == req_country

    def _currency_for_locality(self, locality: str) -> Dict[str, str]:
        if not locality:
            country = "us"
        else:
            parts = locality.split("-")
            if parts[0] == "online" and len(parts) > 1:
                country = parts[1]
            else:
                country = parts[0]
        return self._CURRENCY_BY_COUNTRY.get(country, {"code": "USD", "symbol": "$"})


def summarize_offers(offers: Iterable[Dict[str, object]]) -> Dict[str, object]:
    offers_list = list(offers)
    if not offers_list:
        return {"count": 0, "min_price": None, "max_price": None}
    prices = [offer["price"] for offer in offers_list if isinstance(offer.get("price"), (int, float))]
    prices.sort()
    return {
        "count": len(offers_list),
        "min_price": prices[0] if prices else None,
        "max_price": prices[-1] if prices else None,
    }
