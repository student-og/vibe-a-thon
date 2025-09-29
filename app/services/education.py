"""Educational content and savings estimators for chronic conditions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .i18n import normalize_language_code, translate
from .matching import MedicineMatcher


@dataclass(frozen=True)
class ModuleConfig:
    key: str
    conditions: List[str]
    featured_medicines: List[str]


class EducationLibrary:
    """Surface condition-specific learning modules and savings insights."""

    _MODULES: List[ModuleConfig] = [
        ModuleConfig(
            key="ui.education.modules.diabetes",
            conditions=["type-2-diabetes", "prediabetes"],
            featured_medicines=["Metformin", "Jardiance", "Farxiga", "Ozempic"],
        ),
        ModuleConfig(
            key="ui.education.modules.hypertension",
            conditions=["hypertension", "cardiovascular-risk"],
            featured_medicines=["Lisinopril", "Amlodipine", "Losartan"],
        ),
        ModuleConfig(
            key="ui.education.modules.asthma",
            conditions=["asthma", "copd"],
            featured_medicines=["Symbicort", "Advair", "Albuterol"],
        ),
    ]

    def __init__(self, matcher: MedicineMatcher) -> None:
        self._matcher = matcher

    def get_modules(self, lang: str | None = None) -> List[Dict[str, object]]:
        normalized = normalize_language_code(lang)
        modules: List[Dict[str, object]] = []
        for module in self._MODULES:
            tips = translate(f"{module.key}.tips", normalized)
            if not isinstance(tips, list):
                tips = [tips]
            modules.append(
                {
                    "key": module.key,
                    "conditions": module.conditions,
                    "title": translate(f"{module.key}.title", normalized),
                    "summary": translate(f"{module.key}.summary", normalized),
                    "tips": tips,
                    "featured_medicines": [med for med in module.featured_medicines if self._matcher.find_by_brand_or_generic(med)],
                }
            )
        return modules

    def calculate_savings(
        self,
        medicine_name: str,
        *,
        months: int = 12,
        monthly_quantity: float = 1.0,
        lang: str | None = None,
    ) -> Dict[str, object]:
        if not medicine_name:
            raise ValueError(translate("ui.feedback.enter_more", lang))
        if months <= 0 or monthly_quantity <= 0:
            raise ValueError("Months and quantity must be positive values.")

        medicine = self._matcher.find_by_brand_or_generic(medicine_name)
        if not medicine:
            raise ValueError(translate("ui.feedback.none", lang))

        brand_price = float(medicine.get("average_brand_price") or 0.0)
        generic_price = float(medicine.get("average_generic_price") or 0.0)
        monthly_brand_cost = round(brand_price * monthly_quantity, 2)
        monthly_generic_cost = round(generic_price * monthly_quantity, 2)
        monthly_savings = round(monthly_brand_cost - monthly_generic_cost, 2)
        total_savings = round(monthly_savings * months, 2)

        normalized = normalize_language_code(lang)
        return {
            "medicine": medicine["brand_name"],
            "generic": medicine["generic_name"],
            "months": months,
            "monthly_quantity": monthly_quantity,
            "monthly_brand_cost": monthly_brand_cost,
            "monthly_generic_cost": monthly_generic_cost,
            "monthly_savings": monthly_savings,
            "total_savings": total_savings,
            "advice": translate("advice", normalized),
            "assumptions": {
                "note": "Average prices represent a 30-day fill; quantity scales packs per month.",
            },
        }
