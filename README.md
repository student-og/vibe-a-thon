# Generic vs. Branded Medicine Finder

This project is a lightweight web experience that helps users discover cost-effective generic alternatives to popular branded medicines. It highlights potential savings, showcases educational context, and demonstrates how improved awareness can reduce overspending.

## Features

- 🔍 **Search by brand or generic name** with fuzzy matching to surface relevant results.
- 💰 **Transparent price comparison** between branded and generic versions with estimated savings.
- 📊 **Dataset insights** showing overall coverage and average savings across the catalog.
- 📚 **Educational notes and sources** linking to reputable health organizations for further reading.

## Getting Started

### 1. Set up the environment

```bash
python -m venv .venv
source .venv/bin/activate
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

## Project structure

```
.
├── app
│   ├── __init__.py          # Flask application factory
│   ├── api.py               # HTTP routes and API endpoints
│   ├── data
│   │   └── medicines.json   # Curated dataset of branded/generic medicines
│   ├── services
│   │   └── matching.py      # Matching logic and search utilities
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

## Extending the experience

- Upload a richer dataset from regulatory APIs (e.g., FDA Orange Book, openFDA).
- Surface nearby pharmacies or online retailers with up-to-date pricing.
- Add multilingual support to broaden accessibility.
- Integrate educational modules or savings calculators for chronic conditions.

Always advise users to consult their healthcare providers before changing medications.