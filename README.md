# Generic vs. Branded Medicine Finder

A comprehensive web application that helps users discover affordable generic alternatives to branded medicines, featuring enhanced regulatory data, pharmacy finder, educational resources, and multilingual support.

![Enhanced Medicine Finder](https://github.com/user-attachments/assets/7981455a-2433-43a0-aca6-210efc80c63f)

## ✨ Features

### 🔍 **Medicine Search & Comparison**
- Search by branded or generic medicine names
- Comprehensive price comparison with savings calculations
- Detailed medicine information including indications, forms, and strengths
- FDA Orange Book integration for regulatory compliance

### 🏥 **Pharmacy Finder**
- Locate nearby pharmacies based on ZIP code or city
- Filter by pricing tier (low, medium, high)
- Pharmacy details including services, hours, and contact information
- Distance calculation and routing information

### 🌍 **Multilingual Support**
- English, Spanish, French, German, and Chinese language options
- Localized pricing adjustments for different regions
- Culturally appropriate healthcare messaging

### 📚 **Educational Resources**
- **Understanding Generic Medicines**: FDA approval process, bioequivalence, quality standards
- **Chronic Care Management**: Resources for diabetes, hypertension, cholesterol management
- **Savings Tips**: Practical advice for reducing prescription costs
- **FDA Approval Process**: Detailed information about generic drug regulation

### 💰 **Savings Calculator**
- Calculate annual savings when switching to generics
- Support for chronic condition medications
- Prescription frequency customization
- Detailed cost breakdown with percentage savings

### ⚠️ **Healthcare Safety**
- Prominent healthcare disclaimers throughout the application
- Consistent messaging about consulting healthcare providers
- Safety notices on all medication results

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/student-og/vibe-a-thon.git
   cd vibe-a-thon
   ```

2. **Set up the environment**
   
   **For Linux/Unix:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   
   **For Windows (PowerShell):**
   ```bash
   python -m venv .venv
   . .venv\Scripts\Activate
   pip install -r requirements.txt
   ```
   
   **For Windows (Command Prompt):**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```

3. **Run the development server**
   ```bash
   python run.py
   ```

4. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest -v

# Or simply
pytest
```

Test coverage includes:
- Medicine search and matching functionality
- Pharmacy finder with location-based filtering
- Educational content delivery
- Savings calculator with various scenarios
- API error handling and validation

## 🏗️ Project Structure

```
vibe-a-thon/
├── app/
│   ├── __init__.py                 # Flask application factory
│   ├── api.py                      # HTTP endpoints and API routes
│   ├── data/
│   │   └── medicines.json          # Enhanced medicine database with FDA data
│   ├── services/
│   │   ├── matching.py             # Medicine matching and search logic
│   │   └── pharmacy_finder.py      # Pharmacy location and pricing service
│   ├── static/
│   │   ├── app.js                  # Enhanced frontend with i18n and calculators
│   │   └── styles.css              # Responsive CSS with new components
│   └── templates/
│       └── index.html              # Enhanced UI with education and tools
├── tests/
│   ├── test_api.py                 # Original API tests
│   └── test_new_features.py        # Tests for new functionality
├── requirements.txt                # Python dependencies
├── run.py                          # Application entry point
└── README.md                       # This documentation
```

## 🔌 API Endpoints

### Medicine Search
- `GET /api/medicines?q={query}&locality={location}` - Search medicines
- `GET /api/medicines/{name}` - Get specific medicine details
- `GET /api/medicines/{name}/alternatives` - Get alternative medicines

### Pharmacy Finder
- `GET /api/pharmacies?location={location}&pricing={tier}&limit={count}` - Find nearby pharmacies
- `GET /api/pharmacies/{name}` - Get pharmacy details

### Educational Content
- `GET /api/education/{topic}` - Get educational content
  - Topics: `generic-medicines`, `chronic-conditions`, `savings-tips`, `fda-approval`

### Savings Calculator
- `POST /api/calculate-savings` - Calculate annual savings
  ```json
  {
    "brand_price": 190.0,
    "generic_price": 12.5,
    "prescriptions_per_year": 12,
    "medicine_name": "Lipitor"
  }
  ```

## 📊 Enhanced Data Sources

The application now integrates with multiple regulatory and healthcare data sources:

- **FDA Orange Book**: Official generic drug approvals and bioequivalence ratings
- **openFDA**: Real-time drug pricing and availability data
- **WHO Essential Medicines List**: Global medicine standards and recommendations
- **CDC Generic Drug Facts**: Safety and efficacy information
- **National Library of Medicine**: Research and clinical data

## 🌐 Internationalization

The application supports multiple languages with culturally appropriate content:

- **English**: Default language with US pricing
- **Español**: Spanish translations with regional pricing adjustments
- **Français**: French translations with European regulatory context
- **Deutsch**: German translations with EU medicine standards
- **中文**: Chinese translations with local healthcare practices

## 🔒 Healthcare Compliance

The application prioritizes patient safety with:

- **Prominent Disclaimers**: Healthcare provider consultation warnings on every page
- **Regulatory Compliance**: FDA-approved generic alternatives only
- **Educational Focus**: Information rather than medical advice
- **Source Attribution**: Clear citations for all medical information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes following the coding standards
4. Add tests for new functionality
5. Update documentation as needed
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-feature`)
8. Create a Pull Request

### Development Guidelines

- **Healthcare Safety**: Always include appropriate disclaimers
- **Data Accuracy**: Verify all medicine data with authoritative sources
- **Testing**: Maintain high test coverage
- **Documentation**: Update README and API docs for new features
- **Accessibility**: Ensure WCAG 2.1 AA compliance

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Healthcare Notice

**This application is for informational purposes only and should not replace professional medical advice. Always consult your healthcare provider before making any changes to your medications. Generic alternatives must be approved by your doctor.**

---

*Enhanced with regulatory data integration, pharmacy finder, multilingual support, and comprehensive educational resources.*
