"""Lightweight internationalization helpers for the medicine finder experience."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Dict, Iterable, Tuple


_TRANSLATIONS: Dict[str, Dict[str, object]] = {
    "en": {
        "label": "English",
        "direction": "ltr",
        "strings": {
            "advice": "Always consult your healthcare provider before making any medication changes.",
            "ui.hero_title": "Generic vs. Branded Medicine Finder",
            "ui.hero_description": "Compare brand-name prescriptions with therapeutically equivalent generics, localized pricing, and chronic care guidance.",
            "ui.stats.medicines": "Medicines tracked",
            "ui.stats.avg_savings": "Average savings per prescription",
            "ui.stats.brand_price": "Avg. branded price",
            "ui.stats.generic_price": "Avg. generic price",
            "ui.search.label": "Search by branded or generic name",
            "ui.search.placeholder": "e.g., Tylenol, Lipitor, Metformin",
            "ui.search.cta": "Find Alternatives",
            "ui.language.label": "Preferred language",
            "ui.locality.label": "Locality or region code",
            "ui.locality.placeholder": "us-ny, us-ca, in-ka",
            "ui.feedback.enter_more": "Enter at least two characters to search.",
            "ui.feedback.searching": "Searching...",
            "ui.feedback.none": "No matches found. Try a different brand or generic name.",
            "ui.feedback.matches": "{count} matches found.",
            "ui.feedback.single_match": "1 match found.",
            "ui.results.disclaimer": "Pricing reflects average retail fills; verify with your pharmacist for patient-specific costs.",
            "ui.results.sources": "Sources",
            "ui.results.indications": "Indications",
            "ui.results.form": "Form",
            "ui.results.strength": "Strength",
            "ui.results.brand": "Brand",
            "ui.results.generic": "Generic",
            "ui.results.savings": "Savings",
            "ui.pharmacies.title": "Nearby pharmacy and online offers",
            "ui.pharmacies.subtitle": "Compare dispensing partners for the lowest available fill price in your area.",
            "ui.pharmacies.none": "No live offers were found for this medicine in the selected region.",
            "ui.pharmacies.last_updated": "Last updated",
            "ui.pharmacies.delivery": "Delivery",
            "ui.pharmacies.view_site": "View site",
            "ui.education.title": "Chronic condition learning hub",
            "ui.education.subtitle": "Reviewed guidance tailored to diabetes, heart health, asthma, and more.",
            "ui.education.more": "Explore guidance",
            "ui.education.modules.diabetes.title": "Type 2 diabetes: Build a generic-first plan",
            "ui.education.modules.diabetes.summary": "Metformin, SGLT2 inhibitors, and GLP-1 therapies offer diverse options. Pair affordable generics with nutrition, movement, and A1C monitoring.",
            "ui.education.modules.diabetes.tips": [
                "Ask about 90-day generic refills to unlock lower per-pill pricing.",
                "Stack manufacturer savings cards with insurance or discount programs.",
                "Schedule quarterly A1C labs to measure adherence and efficacy."
            ],
            "ui.education.modules.hypertension.title": "Hypertension: Optimize combination therapy",
            "ui.education.modules.hypertension.summary": "ACE inhibitors, ARBs, and thiazide diuretics have proven, low-cost generic options. Monitor blood pressure at home to dial-in dosing.",
            "ui.education.modules.hypertension.tips": [
                "Switching to fixed-dose generic combos can reduce copays and pill burden.",
                "Home blood pressure logs help clinicians adjust therapy earlier.",
                "Ask about once-daily generics to improve adherence."
            ],
            "ui.education.modules.asthma.title": "Asthma & COPD: Smart inhaler strategies",
            "ui.education.modules.asthma.summary": "Maintenance inhalers (ICS/LABA) now have competitive generics; rescue inhalers remain essential. Align spacers and action plans with your care team.",
            "ui.education.modules.asthma.tips": [
                "Verify inhaler technique every visit for optimal deposition.",
                "Capture peak flow trends to anticipate exacerbations.",
                "Pair controller generics with digital reminders for daily adherence."
            ],
            "ui.savings.title": "Savings calculator",
            "ui.savings.medicine_label": "Medicine",
            "ui.savings.months_label": "Months on therapy",
            "ui.savings.quantity_label": "Monthly fills (packs)",
            "ui.savings.submit": "Estimate savings",
            "ui.savings.result": "Estimated total savings",
            "ui.savings.input_hint": "Use the search results or type any supported medicine.",
            "ui.footer.disclaimer": "Data sourced from public drug registries and price benchmarks. Always consult your healthcare provider before making medication changes."
        },
    },
    "es": {
        "label": "Español",
        "direction": "ltr",
        "strings": {
            "advice": "Siempre consulte a su profesional de salud antes de cambiar cualquier medicamento.",
            "ui.hero_title": "Buscador de Medicamentos Genéricos y de Marca",
            "ui.hero_description": "Compare recetas de marca con equivalentes genéricos, precios localizados y orientación para enfermedades crónicas.",
            "ui.stats.medicines": "Medicamentos registrados",
            "ui.stats.avg_savings": "Ahorro promedio por receta",
            "ui.stats.brand_price": "Precio promedio de marca",
            "ui.stats.generic_price": "Precio promedio genérico",
            "ui.search.label": "Buscar por nombre comercial o genérico",
            "ui.search.placeholder": "p. ej., Tylenol, Lipitor, Metformina",
            "ui.search.cta": "Encontrar alternativas",
            "ui.language.label": "Idioma preferido",
            "ui.locality.label": "Código de región o localidad",
            "ui.locality.placeholder": "us-ny, us-ca, in-ka",
            "ui.feedback.enter_more": "Introduzca al menos dos caracteres para buscar.",
            "ui.feedback.searching": "Buscando...",
            "ui.feedback.none": "No se encontraron resultados. Pruebe con otro nombre comercial o genérico.",
            "ui.feedback.matches": "{count} resultados encontrados.",
            "ui.feedback.single_match": "1 resultado encontrado.",
            "ui.results.disclaimer": "Los precios reflejan promedios minoristas; verifique con su farmacia para costos específicos.",
            "ui.results.sources": "Fuentes",
            "ui.results.indications": "Indicaciones",
            "ui.results.form": "Forma",
            "ui.results.strength": "Concentración",
            "ui.results.brand": "Marca",
            "ui.results.generic": "Genérico",
            "ui.results.savings": "Ahorro",
            "ui.pharmacies.title": "Ofertas cercanas y minoristas en línea",
            "ui.pharmacies.subtitle": "Compare distribuidores para encontrar el precio más bajo en su zona.",
            "ui.pharmacies.none": "No se encontraron ofertas para esta medicina en la región seleccionada.",
            "ui.pharmacies.last_updated": "Actualizado",
            "ui.pharmacies.delivery": "Entrega",
            "ui.pharmacies.view_site": "Visitar sitio",
            "ui.education.title": "Centro de aprendizaje para enfermedades crónicas",
            "ui.education.subtitle": "Orientación revisada para diabetes, salud cardíaca, asma y más.",
            "ui.education.more": "Explorar orientación",
            "ui.education.modules.diabetes.title": "Diabetes tipo 2: Diseñe un plan enfocado en genéricos",
            "ui.education.modules.diabetes.summary": "La metformina, los inhibidores SGLT2 y las terapias GLP-1 ofrecen opciones diversas. Combine genéricos asequibles con nutrición, actividad y control de A1C.",
            "ui.education.modules.diabetes.tips": [
                "Solicite resurtidos genéricos para 90 días y reduzca el costo por tableta.",
                "Combine tarjetas de ahorro de fabricantes con seguro o programas de descuento.",
                "Programe análisis de A1C trimestrales para medir adherencia y eficacia."
            ],
            "ui.education.modules.hypertension.title": "Hipertensión: Optimice la terapia combinada",
            "ui.education.modules.hypertension.summary": "Los IECA, ARA II y diuréticos tiazídicos tienen opciones genéricas de bajo costo. Controle la presión arterial en casa para ajustar la dosis.",
            "ui.education.modules.hypertension.tips": [
                "Los comprimidos combinados genéricos reducen copagos y cantidad de pastillas.",
                "Los registros de presión arterial en casa ayudan a ajustar la terapia más pronto.",
                "Pregunte por genéricos de una dosis diaria para mejorar la adherencia."
            ],
            "ui.education.modules.asthma.title": "Asma y EPOC: Estrategias inteligentes con inhaladores",
            "ui.education.modules.asthma.summary": "Los inhaladores de mantenimiento (ICS/LABA) ya tienen genéricos competitivos; los inhaladores de rescate siguen siendo esenciales.",
            "ui.education.modules.asthma.tips": [
                "Verifique la técnica del inhalador en cada visita para lograr una mejor administración.",
                "Registre el flujo máximo para anticipar exacerbaciones.",
                "Combine los genéricos de mantenimiento con recordatorios digitales diarios."
            ],
            "ui.savings.title": "Calculadora de ahorro",
            "ui.savings.medicine_label": "Medicamento",
            "ui.savings.months_label": "Meses en tratamiento",
            "ui.savings.quantity_label": "Resurtidos mensuales (paquetes)",
            "ui.savings.submit": "Estimar ahorro",
            "ui.savings.result": "Ahorro total estimado",
            "ui.savings.input_hint": "Use los resultados de búsqueda o escriba cualquier medicamento compatible.",
            "ui.footer.disclaimer": "Datos de registros públicos y referencias de precios. Consulte siempre a su profesional de salud antes de cambiar medicamentos."
        },
    },
    "hi": {
        "label": "हिन्दी",
        "direction": "ltr",
        "strings": {
            "advice": "किसी भी दवा में बदलाव से पहले हमेशा अपने स्वास्थ्य प्रदाता से सलाह लें।",
            "ui.hero_title": "जनरिक बनाम ब्रांडेड दवा खोजें",
            "ui.hero_description": "ब्रांडेड दवाओं की तुलना चिकित्सकीय समकक्ष जनरिक विकल्पों, स्थानीय मूल्य और दीर्घकालिक देखभाल मार्गदर्शन के साथ करें।",
            "ui.stats.medicines": "ट्रैक की गई दवाएँ",
            "ui.stats.avg_savings": "प्रति पर्चे औसत बचत",
            "ui.stats.brand_price": "औसत ब्रांड कीमत",
            "ui.stats.generic_price": "औसत जनरिक कीमत",
            "ui.search.label": "ब्रांड या जनरिक नाम से खोजें",
            "ui.search.placeholder": "उदा. टायलिनोल, लिपिटोर, मेटफॉर्मिन",
            "ui.search.cta": "विकल्प खोजें",
            "ui.language.label": "पसंदीदा भाषा",
            "ui.locality.label": "क्षेत्र कोड",
            "ui.locality.placeholder": "us-ny, us-ca, in-ka",
            "ui.feedback.enter_more": "खोज के लिए कम से कम दो अक्षर दर्ज करें।",
            "ui.feedback.searching": "खोज जारी है...",
            "ui.feedback.none": "कोई परिणाम नहीं मिला। कोई दूसरा नाम आज़माएँ।",
            "ui.feedback.matches": "{count} परिणाम मिले।",
            "ui.feedback.single_match": "1 परिणाम मिला।",
            "ui.results.disclaimer": "कीमतें औसत खुदरा मूल्य दर्शाती हैं; सटीक जानकारी के लिए अपने फार्मासिस्ट से जाँच करें।",
            "ui.results.sources": "स्रोत",
            "ui.results.indications": "प्रयोग",
            "ui.results.form": "रूप",
            "ui.results.strength": "ताकत",
            "ui.results.brand": "ब्रांड",
            "ui.results.generic": "जनरिक",
            "ui.results.savings": "बचत",
            "ui.pharmacies.title": "निकटतम फ़ार्मेसी और ऑनलाइन ऑफ़र",
            "ui.pharmacies.subtitle": "अपने क्षेत्र में उपलब्ध न्यूनतम मूल्य की तुलना करें।",
            "ui.pharmacies.none": "निर्दिष्ट क्षेत्र में कोई ऑफ़र नहीं मिला।",
            "ui.pharmacies.last_updated": "अंतिम अद्यतन",
            "ui.pharmacies.delivery": "डिलीवरी",
            "ui.pharmacies.view_site": "साइट देखें",
            "ui.education.title": "दीर्घकालिक रोग शिक्षण केंद्र",
            "ui.education.subtitle": "मधुमेह, हृदय स्वास्थ्य, अस्थमा आदि के लिए तैयार मार्गदर्शन।",
            "ui.education.more": "मार्गदर्शन देखें",
            "ui.education.modules.diabetes.title": "टाइप 2 मधुमेह: जनरिक-प्रथम योजना",
            "ui.education.modules.diabetes.summary": "मेटफॉर्मिन, SGLT2 और GLP-1 उपचारों के जनरिक विकल्प उपलब्ध हैं। पोषण, व्यायाम और A1C मॉनिटरिंग के साथ जोड़ें।",
            "ui.education.modules.diabetes.tips": [
                "90 दिन की जनरिक दवाओं की आपूर्ति पर लागत कम होती है।",
                "निर्माता बचत कार्ड को बीमा या छूट कार्यक्रमों के साथ मिलाएँ।",
                "प्रत्येक तिमाही में A1C जाँच करवाएँ।"
            ],
            "ui.education.modules.hypertension.title": "उच्च रक्तचाप: संयोजन थेरेपी का अनुकूलन",
            "ui.education.modules.hypertension.summary": "ACE इन्हिबिटर, ARB और थायाजाइड डाययूरेटिक के सस्ते जनरिक विकल्प उपलब्ध हैं।",
            "ui.education.modules.hypertension.tips": [
                "स्थायी खुराक वाले जनरिक संयोजन गोलियाँ कॉपे और गोली की संख्या कम करती हैं।",
                "घर पर रक्तचाप दर्ज करने से डॉक्टर उपचार जल्दी समायोजित कर सकते हैं।",
                "दिन में एक बार लेने वाले जनरिक विकल्पों से पालन बेहतर होता है।"
            ],
            "ui.education.modules.asthma.title": "अस्थमा व COPD: स्मार्ट इनहेलर रणनीति",
            "ui.education.modules.asthma.summary": "ICS/LABA मेंटेनेंस इनहेलेर्स के किफायती जनरिक उपलब्ध हैं; रेस्क्यू इनहेलेर आवश्यक हैं।",
            "ui.education.modules.asthma.tips": [
                "प्रत्येक मुलाकात पर इनहेलेर तकनीक की समीक्षा करें।",
                "पीक फ्लो रीडिंग दर्ज करें ताकि अटैक का अनुमान लगाया जा सके।",
                "दैनिक याद दिलाने वाले ऐप्स के साथ नियंत्रक जनरिक्स का उपयोग करें।"
            ],
            "ui.savings.title": "बचत कैलकुलेटर",
            "ui.savings.medicine_label": "दवा",
            "ui.savings.months_label": "उपचार के महीने",
            "ui.savings.quantity_label": "मासिक पैक",
            "ui.savings.submit": "बचत अनुमानित करें",
            "ui.savings.result": "अनुमानित कुल बचत",
            "ui.savings.input_hint": "खोज परिणाम का उपयोग करें या कोई भी समर्थित दवा दर्ज करें।",
            "ui.footer.disclaimer": "जानकारी सार्वजनिक दवा रजिस्ट्रियों और मूल्य संदर्भों से ली गई है। दवा बदलने से पहले डॉक्टर से सलाह लें।"
        },
    },
}


def normalize_language_code(language: str | None) -> str:
    """Return a supported language code (defaults to English)."""
    if not language:
        return "en"
    code = language.lower()
    if code in _TRANSLATIONS:
        return code
    short = code.split("-")[0]
    if short in _TRANSLATIONS:
        return short
    return "en"


def translate(key: str, language: str | None = None) -> str:
    """Translate the given key, falling back to English when missing."""
    normalized = normalize_language_code(language)
    strings = _TRANSLATIONS[normalized]["strings"]  # type: ignore[index]
    if key in strings:
        return strings[key]  # type: ignore[return-value]
    # fall back to English and finally the key itself
    default_strings = _TRANSLATIONS["en"]["strings"]  # type: ignore[index]
    return default_strings.get(key, key)  # type: ignore[return-value]


def get_supported_languages() -> Iterable[Dict[str, str]]:
    """Return the available languages for selection in the UI."""
    return (
        {
            "code": code,
            "label": payload["label"],
            "direction": payload.get("direction", "ltr"),
        }
        for code, payload in _TRANSLATIONS.items()
    )


def get_translations(language: str | None = None) -> Dict[str, str]:
    """Return all translation strings for a single language."""
    normalized = normalize_language_code(language)
    strings = _TRANSLATIONS[normalized]["strings"]  # type: ignore[index]
    return dict(strings)  # shallow copy to prevent mutation


def get_all_translations() -> Dict[str, Dict[str, str]]:
    """Return translations for all supported languages."""
    return {code: dict(cfg["strings"]) for code, cfg in _TRANSLATIONS.items()}


def build_metadata(language: str | None = None) -> Dict[str, object]:
    """Return metadata payload for API consumers."""
    normalized = normalize_language_code(language)
    return {
        "language": normalized,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "supported": list(get_supported_languages()),
    }


def require_language(language: str | None) -> Tuple[str, Dict[str, str]]:
    """Return a normalized language code and its translation dictionary."""
    normalized = normalize_language_code(language)
    strings = get_translations(normalized)
    return normalized, strings