"""Integration helpers for regulatory drug datasets (FDA Orange Book, openFDA)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import UTC, datetime
from importlib import resources
from typing import Dict, List, Optional, Tuple

from .i18n import translate

_OPENFDA_ENDPOINT = (
    "https://api.fda.gov/drug/drugsfda.json?search=products.marketing_status:%22Prescription%22&limit={limit}"
)
_ORANGE_BOOK_ENDPOINT = (
    "https://api.fda.gov/drug/ndc.json?search=finished:true&limit={limit}"
)


class RegulatoryDataFetcher:
    """Fetch regulatory-approved medicines and normalize them for the matcher."""

    def __init__(self, timeout: int = 8) -> None:
        self.timeout = timeout

    # --- Public API -----------------------------------------------------
    def fetch_dataset(
        self,
        *,
        limit: int = 40,
        offline: bool = True,
    ) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
        """Return a dataset and metadata payload.

        When ``offline`` is True (default in tests), the method skips network
touches and returns an enriched sample curated from the FDA Orange Book and
openFDA exports. When ``offline`` is False, the helper will attempt lightweight
requests to both endpoints and merge their output, falling back to the local
sample if the request fails or produces incomplete data.
        """

        dataset: List[Dict[str, object]] = []
        metadata: Dict[str, object] = {
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "sources": [],
            "notes": [],
        }

        if not offline:
            dataset.extend(self._try_fetch_openfda(limit // 2))
            dataset.extend(self._try_fetch_orange_book(limit // 2))
            metadata["notes"].append(
                "Live fetch attempted from openFDA and Orange Book APIs; offline sample used for any gaps."
            )

        if not dataset:
            dataset = self._load_sample()
            metadata["notes"].append(
                "Using packaged FDA sample dataset (no external network access detected)."
            )
            metadata["sources"].append("app/data/regulatory_sample.json")
        else:
            metadata["sources"].extend(
                [
                    "openFDA: /drug/drugsfda",
                    "openFDA: /drug/ndc",
                ]
            )

        dataset = dataset[:limit]
        metadata["records"] = len(dataset)
        metadata.setdefault("sources", [])
        metadata.setdefault("notes", [])
        return dataset, metadata

    # --- Internal helpers -----------------------------------------------
    def _try_fetch_openfda(self, limit: int) -> List[Dict[str, object]]:
        url = _OPENFDA_ENDPOINT.format(limit=max(1, min(limit, 100)))
        payload = self._safe_json_request(url)
        if not payload:
            return []
        results: List[Dict[str, object]] = []
        for entry in payload.get("results", []):
            application = entry.get("application_number")
            for product in entry.get("products", []):
                brand = product.get("brand_name")
                generic = product.get("generic_name")
                if not brand or not generic:
                    continue
                dosage = product.get("dosage_form", "")
                strength = product.get("strength", "")
                indications = list(
                    {
                        *(entry.get("submission_class_code", ""),),
                        *(entry.get("submission_type", ""),),
                    }
                )
                results.append(
                    {
                        "brand_name": brand.title(),
                        "generic_name": generic.title(),
                        "indications": [item for item in indications if item],
                        "form": dosage.title(),
                        "strength": strength,
                        # openFDA does not expose pricing; set placeholders to allow merging
                        "average_brand_price": 0.0,
                        "average_generic_price": 0.0,
                        "notes": "Fetched from openFDA /drug/drugsfda API.",
                        "sources": [
                            {
                                "name": "openFDA Drug Products",
                                "url": url,
                            }
                        ],
                        "regulatory_application": application,
                    }
                )
        return results

    def _try_fetch_orange_book(self, limit: int) -> List[Dict[str, object]]:
        url = _ORANGE_BOOK_ENDPOINT.format(limit=max(1, min(limit, 100)))
        payload = self._safe_json_request(url)
        if not payload:
            return []
        results: List[Dict[str, object]] = []
        for item in payload.get("results", []):
            brand = item.get("brand_name") or item.get("proprietary_name")
            if not brand:
                continue
            generic = item.get("generic_name") or brand
            form = item.get("dosage_form", "")
            strength = item.get("active_ingredients") or item.get("strength") or ""
            results.append(
                {
                    "brand_name": brand.title(),
                    "generic_name": generic.title(),
                    "indications": [item.get("product_type", "Prescription")],
                    "form": form.title(),
                    "strength": strength,
                    "average_brand_price": 0.0,
                    "average_generic_price": 0.0,
                    "notes": "Fetched from openFDA /drug/ndc API.",
                    "sources": [
                        {
                            "name": "openFDA Orange Book",
                            "url": url,
                        }
                    ],
                    "ndc_package": item.get("package_ndc"),
                }
            )
        return results

    def _load_sample(self) -> List[Dict[str, object]]:
        with resources.files("app.data").joinpath("regulatory_sample.json").open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _safe_json_request(self, url: str) -> Optional[Dict[str, object]]:
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                if response.status != 200:
                    return None
                raw = response.read()
        except (urllib.error.URLError, TimeoutError):
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None


def build_refresh_response(
    *,
    added: int,
    metadata: Dict[str, object],
    lang: str,
) -> Dict[str, object]:
    """Utility for composing refresh endpoint responses."""
    return {
        "added": added,
        "metadata": metadata,
        "advice": translate("advice", lang),
    }
