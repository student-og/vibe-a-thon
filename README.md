# Generic vs. Branded Medicine Finder

This project is a lightweight web experience that helps users discover cost-effective generic alternatives to popular branded medicines. It highlights potential savings, showcases educational context, and demonstrates how improved awareness can reduce overspending.

## Features

- 🔍 **Search by brand or generic name** with fuzzy matching to surface relevant results.
- 💰 **Transparent price comparison** between branded and generic versions with estimated savings.
- 📊 **Dataset insights** showing overall coverage and average savings across the catalog.
- �️ **Regulatory data enrichment** via FDA Orange Book / openFDA with an offline sample fallback for quick demos.
- 🏥 **Nearby pharmacy & online offers** with locality-aware pricing multipliers and live refresh timestamps.
- 🌍 **Multilingual experience** (English, Español, हिन्दी) with dynamic UI translations and localized advisories.
- 📚 **Educational notes, chronic care modules, and savings calculator** geared toward diabetes, hypertension, asthma, and more.

## Getting Started

### 1. Set up the environment
***for linux/unix
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
***for windows
In PowerShell, you should activate a Python virtual environment with:
```bash
python -m venv .venv
. .venv\Scripts\Activate
pip install -r requirements.txt
```
Or, if you're using Command Prompt (cmd.exe):
```bash
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 2. Run the development server

```bash
python run.py
```

The site will be available at <http://localhost:5000/>.

## Running the test suite

```bash
pytest
```
or 
```bash
python -m pytest
```

## Project structure

```
.
├── app
│   ├── __init__.py          # Flask application factory
│   ├── api.py               # HTTP routes and API endpoints
│   ├── data
│   │   ├── medicines.json            # Curated dataset of branded/generic medicines
│   │   └── regulatory_sample.json    # FDA-enriched sample used when offline
│   ├── services
│   │   ├── education.py     # Chronic condition modules and savings estimates
│   │   ├── i18n.py          # Translation dictionaries and helpers
│   │   ├── matching.py      # Matching logic and search utilities
│   │   ├── pharmacy.py      # Simulated pharmacy locator with pricing adjustments
│   │   └── regulatory.py    # Regulatory API integration helpers
│   ├── static
│   │   ├── app.js           # Front-end interactions
│   │   └── styles.css       # UI styling
│   └── templates
│       └── index.html       # Landing page template
├── run.py                   # Local development entry point
├── requirements.txt         # Python dependencies
└── tests
	└── test_api.py          # API regression tests
```
## API enhancements

All endpoints continue to include the original search experience, now with additional capabilities:

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/medicines` | GET | Search branded/generic medicines. Supports `lang` and `locality` for localized advice and price adjustments. |
| `/api/medicines/<name>` | GET | Detailed view with optional alternatives. |
| `/api/medicines/<name>/pharmacies` | GET | Local pharmacy and online partner offers with pricing snapshots. |
| `/api/dataset/refresh` | POST | Pull and merge an enriched dataset from regulatory APIs (offline sample by default). |
| `/api/education/modules` | GET | Chronic condition learning modules tailored to the selected language. |
| `/api/education/savings` | POST | Estimate savings for chronic therapy using brand vs. generic averages. |
| `/api/i18n` | GET | Retrieve translation dictionaries and supported languages for the UI. |

> **Reminder:** Always advise users to consult their healthcare providers before changing medications.
Always advise users to consult their healthcare providers before changing medications.
