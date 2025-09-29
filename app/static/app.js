// Internationalization support
const translations = {
  en: {
    'searching': 'Searching...',
    'matches_found': 'matches found.',
    'match_found': 'match found.',
    'no_matches': 'No matches found. Try searching for another brand or generic name.',
    'disclaimer': 'Always consult your healthcare provider before changing medications.',
    'nearby_pharmacies': 'Nearby Pharmacies',
    'finding_pharmacies': 'Finding nearby pharmacies...'
  },
  es: {
    'searching': 'Buscando...',
    'matches_found': 'coincidencias encontradas.',
    'match_found': 'coincidencia encontrada.',
    'no_matches': 'No se encontraron coincidencias. Intenta buscar otro nombre de marca o genérico.',
    'disclaimer': 'Siempre consulte a su proveedor de atención médica antes de cambiar medicamentos.',
    'nearby_pharmacies': 'Farmacias Cercanas',
    'finding_pharmacies': 'Buscando farmacias cercanas...'
  },
  fr: {
    'searching': 'Recherche...',
    'matches_found': 'correspondances trouvées.',
    'match_found': 'correspondance trouvée.',
    'no_matches': 'Aucune correspondance trouvée. Essayez de rechercher un autre nom de marque ou générique.',
    'disclaimer': 'Consultez toujours votre fournisseur de soins de santé avant de changer de médicaments.',
    'nearby_pharmacies': 'Pharmacies à Proximité',
    'finding_pharmacies': 'Recherche de pharmacies à proximité...'
  }
};

let currentLanguage = 'en';

function t(key) {
  return translations[currentLanguage][key] || translations['en'][key] || key;
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("search-form");
  const input = document.getElementById("search-input");
  const locationInput = document.getElementById("location-input");
  const languageSelect = document.getElementById("language-select");
  const resultsContainer = document.getElementById("results");
  const feedback = document.getElementById("search-feedback");

  // Language change handler
  languageSelect.addEventListener("change", (event) => {
    currentLanguage = event.target.value;
    updateLanguage();
  });

  function updateLanguage() {
    // Update placeholders and text based on current language
    // This is a simplified implementation - in a real app you'd use a proper i18n library
    const disclaimers = document.querySelectorAll('.healthcare-disclaimer p');
    disclaimers.forEach(p => {
      if (p.textContent.includes('Always consult')) {
        p.innerHTML = `<strong>${t('disclaimer')}</strong>`;
      }
    });
  }

  const renderResults = (data) => {
    if (!data.results || data.results.length === 0) {
      resultsContainer.innerHTML = `
        <div class="result-card">
          <p>${t('no_matches')}</p>
        </div>`;
      return;
    }

    const html = data.results
      .map((item) => {
        const indications = item.indications
          .map((indication) => `<li>${indication}</li>`)
          .join("");

        const sources = item.sources
          .map(
            (source) =>
              `<li><a href="${source.url}" target="_blank" rel="noopener">${source.name}</a></li>`
          )
          .join("");

        const savings =
          typeof item.savings === "number"
            ? `<span class="price-tag"><strong>Savings</strong>$${item.savings.toFixed(2)}</span>`
            : "";

        return `
          <article class="result-card">
            <header>
              <h3>${item.brand_name}</h3>
              <span class="chip">Generic: ${item.generic_name}</span>
            </header>
            <div class="price-comparison">
              <span class="price-tag"><strong>Brand</strong>$${item.average_brand_price.toFixed(2)}</span>
              <span class="price-tag"><strong>Generic</strong>$${item.average_generic_price.toFixed(2)}</span>
              ${savings}
            </div>
            <p><strong>Form:</strong> ${item.form} &middot; <strong>Strength:</strong> ${item.strength}</p>
            <p><strong>Indications:</strong></p>
            <ul class="indications">${indications}</ul>
            ${
              item.notes
                ? `<p class="notes">${item.notes}</p>`
                : ""
            }
            ${
              sources
                ? `<div class="sources"><strong>Sources:</strong><ul>${sources}</ul></div>`
                : ""
            }
            <div class="healthcare-notice">
              <small><strong>⚠️ ${t('disclaimer')}</strong></small>
            </div>
          </article>`;
      })
      .join("");

    resultsContainer.innerHTML = html;
  };

  async function findNearbyPharmacies(location) {
    // Mock pharmacy finder - in a real implementation, this would call a pharmacy API
    const mockPharmacies = [
      { name: "CVS Pharmacy", address: "123 Main St", distance: "0.5 miles", phone: "(555) 123-4567" },
      { name: "Walgreens", address: "456 Oak Ave", distance: "0.8 miles", phone: "(555) 234-5678" },
      { name: "Walmart Pharmacy", address: "789 Pine Rd", distance: "1.2 miles", phone: "(555) 345-6789" },
      { name: "Rite Aid", address: "321 Elm St", distance: "1.5 miles", phone: "(555) 456-7890" }
    ];

    return new Promise((resolve) => {
      setTimeout(() => resolve(mockPharmacies), 1000);
    });
  }

  function renderPharmacies(pharmacies) {
    const pharmacyHtml = `
      <div class="pharmacy-results">
        <h3>${t('nearby_pharmacies')}</h3>
        ${pharmacies.map(pharmacy => `
          <div class="pharmacy-card">
            <h4>${pharmacy.name}</h4>
            <p>${pharmacy.address}</p>
            <p class="distance">${pharmacy.distance} • ${pharmacy.phone}</p>
          </div>
        `).join('')}
      </div>
    `;
    
    resultsContainer.innerHTML += pharmacyHtml;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = input.value.trim();
    const location = locationInput.value.trim();
    
    if (query.length < 2) {
      feedback.textContent = "Enter at least two characters to search.";
      feedback.classList.remove("visually-hidden");
      return;
    }

    feedback.textContent = t('searching');
    feedback.classList.remove("visually-hidden");

    try {
      const response = await fetch(`/api/medicines?q=${encodeURIComponent(query)}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Unexpected error");
      }

      feedback.textContent = data.count === 1 ? `1 ${t('match_found')}` : `${data.count} ${t('matches_found')}`;
      renderResults(data);

      // Find nearby pharmacies if location is provided
      if (location) {
        feedback.textContent += ` ${t('finding_pharmacies')}`;
        try {
          const pharmacies = await findNearbyPharmacies(location);
          renderPharmacies(pharmacies);
        } catch (error) {
          console.error('Error finding pharmacies:', error);
        }
      }
    } catch (error) {
      feedback.textContent = error.message;
      resultsContainer.innerHTML = "";
    }
  });
});

// Educational Modal Functions
function showEducationalModule(type) {
  const modal = document.getElementById('educational-modal');
  const modalBody = document.getElementById('modal-body');
  
  let content = '';
  
  if (type === 'generic-info') {
    content = `
      <h2>Understanding Generic Medicines</h2>
      <h3>What are Generic Medicines?</h3>
      <p>Generic medicines contain the same active ingredients as brand-name drugs and are proven to work just as well. They must meet the same strict FDA standards for quality, strength, purity, and stability.</p>
      
      <h3>FDA Approval Process</h3>
      <ul>
        <li><strong>Bioequivalence Testing:</strong> Generics must demonstrate they work in the body the same way as the brand-name drug</li>
        <li><strong>Same Active Ingredient:</strong> Must contain identical amounts of the same active ingredient</li>
        <li><strong>Quality Standards:</strong> Manufactured under the same strict cGMP standards as brand drugs</li>
        <li><strong>Same Route of Administration:</strong> Taken the same way (oral, injection, etc.)</li>
      </ul>
      
      <h3>Why Do Generics Cost Less?</h3>
      <p>Generic manufacturers don't have to repeat expensive clinical trials or invest in marketing. This allows them to offer the same medicine at 80-85% less cost than the brand name.</p>
      
      <div class="healthcare-notice">
        <strong>⚠️ Always consult your healthcare provider before switching to generic alternatives.</strong>
      </div>
    `;
  } else if (type === 'chronic-care') {
    content = `
      <h2>Chronic Care Management</h2>
      <h3>Managing Long-term Conditions</h3>
      <p>Chronic conditions require ongoing medication management. Generic alternatives can significantly reduce your healthcare costs over time.</p>
      
      <h3>Common Chronic Conditions & Savings</h3>
      <div class="condition-card">
        <h4>💓 Hypertension (High Blood Pressure)</h4>
        <p>Generic ACE inhibitors and beta-blockers can save $1,200+ annually compared to brand names.</p>
      </div>
      
      <div class="condition-card">
        <h4>🩺 Diabetes</h4>
        <p>Generic Metformin costs about $4/month vs $174/month for brand name - saving over $2,000/year.</p>
      </div>
      
      <div class="condition-card">
        <h4>💊 High Cholesterol</h4>
        <p>Generic statins like Atorvastatin can save $1,800+ annually while providing identical cholesterol-lowering benefits.</p>
      </div>
      
      <h3>Tips for Chronic Care</h3>
      <ul>
        <li>Work with your doctor to identify generic alternatives</li>
        <li>Use 90-day supplies to save more</li>
        <li>Consider mail-order pharmacies for additional savings</li>
        <li>Ask about pharmacy discount programs</li>
      </ul>
      
      <div class="healthcare-notice">
        <strong>⚠️ Never stop or change chronic medications without consulting your healthcare provider.</strong>
      </div>
    `;
  }
  
  modalBody.innerHTML = content;
  modal.style.display = 'flex';
}

function showSavingsCalculator() {
  const modal = document.getElementById('savings-calculator-modal');
  modal.style.display = 'flex';
}

function closeModal() {
  document.getElementById('educational-modal').style.display = 'none';
  document.getElementById('savings-calculator-modal').style.display = 'none';
  document.getElementById('savings-result').style.display = 'none';
}

function calculateSavings() {
  const brandPrice = parseFloat(document.getElementById('brand-price').value);
  const genericPrice = parseFloat(document.getElementById('generic-price').value);
  const prescriptionsPerYear = parseInt(document.getElementById('prescriptions-per-year').value);
  
  if (isNaN(brandPrice) || isNaN(genericPrice) || isNaN(prescriptionsPerYear)) {
    alert('Please fill in all fields with valid numbers.');
    return;
  }
  
  const brandTotal = brandPrice * prescriptionsPerYear;
  const genericTotal = genericPrice * prescriptionsPerYear;
  const annualSavings = brandTotal - genericTotal;
  
  document.getElementById('annual-savings').textContent = annualSavings.toFixed(2);
  document.getElementById('brand-total').textContent = brandTotal.toFixed(2);
  document.getElementById('generic-total').textContent = genericTotal.toFixed(2);
  document.getElementById('savings-result').style.display = 'block';
}

// Close modal when clicking outside
window.addEventListener('click', (event) => {
  const educationalModal = document.getElementById('educational-modal');
  const calculatorModal = document.getElementById('savings-calculator-modal');
  
  if (event.target === educationalModal || event.target === calculatorModal) {
    closeModal();
  }
});
