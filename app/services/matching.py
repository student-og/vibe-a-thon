"""Business logic for matching branded medicines with generic equivalents."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import cached_property
from importlib import resources
from typing import Dict, Iterable, List, Optional


@dataclass(slots=True)
class Medicine:
    brand_name: str
    generic_name: str
    indications: List[str]
    form: str
    strength: str
    average_brand_price: float
    average_generic_price: float
    notes: Optional[str] = None
    sources: Optional[List[Dict[str, str]]] = None

    @property
    def normalized_brand(self) -> str:
        return _normalize(self.brand_name)

    @property
    def normalized_generic(self) -> str:
        return _normalize(self.generic_name)


class MedicineMatcher:
    """Utility for searching medicines."""

    def __init__(self, dataset: Optional[Iterable[Dict[str, object]]] = None) -> None:
        if dataset is None:
            dataset = self._load_default_dataset()
        self._medicines: List[Medicine] = [self._parse(row) for row in dataset if self._is_valid(row)]
        if not self._medicines:
            raise ValueError("No medicines available in dataset")

    def _load_default_dataset(self) -> Iterable[Dict[str, object]]:
        with resources.files("app.data").joinpath("medicines.json").open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _parse(row: Dict[str, object]) -> Medicine:
        return Medicine(
            brand_name=str(row["brand_name"]),
            generic_name=str(row["generic_name"]),
            indications=list(row.get("indications", [])),
            form=str(row.get("form", "")),
            strength=str(row.get("strength", "")),
            average_brand_price=float(row.get("average_brand_price", 0.0)),
            average_generic_price=float(row.get("average_generic_price", 0.0)),
            notes=row.get("notes"),
            sources=row.get("sources"),
        )

    @staticmethod
    def _is_valid(row: Dict[str, object]) -> bool:
        return "brand_name" in row and "generic_name" in row

    def search(self, query: str, limit: int = 10) -> List[Dict[str, object]]:
        """Return the top matches for the provided query."""
        normalized_query = _normalize(query)

        scored: List[tuple[float, Medicine]] = []
        for medicine in self._medicines:
            brand_score = _score(normalized_query, medicine.normalized_brand)
            generic_score = _score(normalized_query, medicine.normalized_generic)
            if brand_score == 0 and generic_score == 0:
                continue
            scored.append((max(brand_score, generic_score), medicine))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [self._to_dict(med) for _, med in scored[:limit]]

    def find_by_brand(self, brand_name: str) -> Optional[Dict[str, object]]:
        normalized = _normalize(brand_name)
        for medicine in self._medicines:
            if medicine.normalized_brand == normalized:
                return self._to_dict(medicine)
        return None

    def get_summary_stats(self) -> Dict[str, object]:
        """Return simple stats for the landing page."""
        prices = [
            (med.average_brand_price, med.average_generic_price)
            for med in self._medicines
            if med.average_brand_price and med.average_generic_price
        ]
        if not prices:
            return {"total_medicines": len(self._medicines)}

        total_brand = sum(pair[0] for pair in prices)
        total_generic = sum(pair[1] for pair in prices)
        avg_brand = round(total_brand / len(prices), 2)
        avg_generic = round(total_generic / len(prices), 2)
        avg_savings = round(avg_brand - avg_generic, 2)

        return {
            "total_medicines": len(self._medicines),
            "average_brand_price": avg_brand,
            "average_generic_price": avg_generic,
            "average_savings": avg_savings,
        }

    @staticmethod
    def _to_dict(medicine: Medicine) -> Dict[str, object]:
        return {
            "brand_name": medicine.brand_name,
            "generic_name": medicine.generic_name,
            "indications": medicine.indications,
            "form": medicine.form,
            "strength": medicine.strength,
            "average_brand_price": medicine.average_brand_price,
            "average_generic_price": medicine.average_generic_price,
            "notes": medicine.notes,
            "sources": medicine.sources or [],
        }

    @cached_property
    def brands(self) -> List[str]:
        return [med.brand_name for med in self._medicines]


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _score(query: str, target: str) -> float:
    if not query or not target:
        return 0.0
    if query in target:
        return 1.0
    ratio = SequenceMatcher(None, query, target).ratio()
    return round(ratio, 2)
