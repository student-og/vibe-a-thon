document.addEventListener("DOMContentLoaded", () => {
  const state = {
    lang: document.documentElement.lang || "en",
    translations: {},
    supportedLanguages: [],
    latestAdvice: "",
    lastSearchResponse: null,
    latestResults: [],
    selectedMedicine: null,
    lastPharmacyResponse: null,
  };

  const elements = {
    form: document.getElementById("search-form"),
    input: document.getElementById("search-input"),
    locality: document.getElementById("locality-input"),
    results: document.getElementById("results"),
    feedback: document.getElementById("search-feedback"),
    adviceBanner: document.getElementById("advice-banner"),
    languageSelect: document.getElementById("language-select"),
    pharmacySection: document.getElementById("pharmacy-section"),
    pharmacyOffers: document.getElementById("pharmacy-offers"),
    modulesContainer: document.getElementById("education-modules"),
    savingsForm: document.getElementById("savings-form"),
    savingsOutput: document.getElementById("savings-output"),
    savingsMedicine: document.getElementById("savings-medicine"),
    savingsMonths: document.getElementById("savings-months"),
    savingsQuantity: document.getElementById("savings-quantity"),
  };

  const t = (key, fallback = "") => {
    const strings = state.translations[state.lang] || state.translations.en || {};
    const value = strings[key];
    if (typeof value === "string") {
      return value;
    }
    return value !== undefined ? value : fallback;
  };

  const ensureTranslations = async () => {
    const response = await fetch(`/api/i18n?lang=${encodeURIComponent(state.lang)}`);
    const data = await response.json();
    state.translations = data.languages || {};
    const metadata = data.metadata || {};
    state.supportedLanguages = metadata.supported || [];
    state.latestAdvice = metadata.advice || t("advice", "");
    applyLanguage(state.lang);
  };

  const applyLanguage = (lang) => {
    state.lang = lang;
    document.documentElement.lang = lang;
    updateLanguageOptions();
    const langMeta = state.supportedLanguages.find((entry) => entry.code === lang);
    document.documentElement.dir = langMeta?.direction || "ltr";
    const strings = state.translations[lang] || state.translations.en || {};
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      const key = node.dataset.i18n;
      if (key && strings[key]) {
        node.textContent = strings[key];
      }
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
      const key = node.dataset.i18nPlaceholder;
      if (key && strings[key]) {
        node.setAttribute("placeholder", strings[key]);
      }
    });
    if (elements.adviceBanner) {
      elements.adviceBanner.textContent = state.latestAdvice || t("advice", elements.adviceBanner.textContent);
    }
    if (state.lastSearchResponse) {
      renderResults(state.lastSearchResponse);
    }
  };

  const updateLanguageOptions = () => {
    if (!elements.languageSelect) return;
    const options = Array.from(elements.languageSelect.options);
    const supported = state.supportedLanguages.length
      ? state.supportedLanguages
      : Object.keys(state.translations).map((code) => ({ code, label: code.toUpperCase(), direction: "ltr" }));
    options.forEach((option) => {
      const match = supported.find((lang) => lang.code === option.value);
      if (match) {
        option.textContent = match.label;
      }
    });
    if (!options.find((option) => option.value === state.lang)) {
      const fallback = (state.translations[state.lang] && state.lang) || "en";
      elements.languageSelect.value = fallback;
    } else {
      elements.languageSelect.value = state.lang;
    }
  };

  const formatPrice = (price, currency) => {
    const symbol = currency?.symbol || "$";
    return `${symbol}${Number(price).toFixed(2)} ${currency?.code || ""}`.trim();
  };

  const renderResults = (data) => {
    state.lastSearchResponse = data;
    state.latestResults = data.results || [];
    elements.results.innerHTML = "";
    if (!data.results || data.results.length === 0) {
      elements.results.innerHTML = `
        <div class="result-card">
          <p>${t("ui.feedback.none", "No matches found. Try searching for another brand or generic name.")}</p>
        </div>`;
      return;
    }

    const brandLabel = t("ui.results.brand", "Brand");
    const genericLabel = t("ui.results.generic", "Generic");
    const savingsLabel = t("ui.results.savings", "Savings");
    const formLabel = t("ui.results.form", "Form");
    const strengthLabel = t("ui.results.strength", "Strength");
    const indicationsLabel = t("ui.results.indications", "Indications");
    const sourcesLabel = t("ui.results.sources", "Sources");

    const cards = data.results
      .map((item) => {
        const indications = (item.indications || [])
          .map((indication) => `<li>${indication}</li>`)
          .join("");
        const sources = (item.sources || [])
          .map(
            (source) =>
              `<li><a href="${source.url}" target="_blank" rel="noopener">${source.name}</a></li>`
          )
          .join("");
        const savings = typeof item.savings === "number"
          ? `<span class="price-tag"><strong>${savingsLabel}</strong>${Number(item.savings).toFixed(2)}</span>`
          : "";

        return `
          <article class="result-card">
            <header>
              <h3>${item.brand_name}</h3>
              <span class="chip">${genericLabel}: ${item.generic_name}</span>
            </header>
            <div class="price-comparison">
              <span class="price-tag"><strong>${brandLabel}</strong>${Number(item.average_brand_price).toFixed(2)}</span>
              <span class="price-tag"><strong>${genericLabel}</strong>${Number(item.average_generic_price).toFixed(2)}</span>
              ${savings}
            </div>
            <p><strong>${formLabel}:</strong> ${item.form} &middot; <strong>${strengthLabel}:</strong> ${item.strength}</p>
            <p><strong>${indicationsLabel}:</strong></p>
            <ul class="indications">${indications}</ul>
            ${item.notes ? `<p class="notes">${item.notes}</p>` : ""}
            ${
              sources
                ? `<div class="sources"><strong>${sourcesLabel}:</strong><ul>${sources}</ul></div>`
                : ""
            }
          </article>`;
      })
      .join("");

    elements.results.innerHTML = cards;

    if (elements.feedback) {
      const feedbackText = data.count === 1
        ? t("ui.feedback.single_match", "1 match found.")
        : t("ui.feedback.matches", "{count} matches found.").replace("{count}", data.count);
      elements.feedback.textContent = feedbackText;
      elements.feedback.classList.remove("visually-hidden");
    }

    if (elements.adviceBanner) {
      elements.adviceBanner.textContent = data.advice || state.latestAdvice || t("advice", elements.adviceBanner.textContent);
    }

    state.selectedMedicine = data.results[0];
    if (state.selectedMedicine && elements.savingsMedicine) {
      elements.savingsMedicine.value = state.selectedMedicine.brand_name;
    }
    if (state.selectedMedicine) {
      fetchPharmacyOffers(state.selectedMedicine.brand_name);
    }
  };

  const fetchPharmacyOffers = async (medicineName) => {
    if (!medicineName) {
      elements.pharmacyOffers.innerHTML = "";
      return;
    }
    const params = new URLSearchParams({ lang: state.lang });
    const locality = elements.locality.value.trim();
    if (locality) {
      params.set("locality", locality);
    }
    try {
      const response = await fetch(`/api/medicines/${encodeURIComponent(medicineName)}/pharmacies?${params.toString()}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Unable to load offers");
      }
      state.lastPharmacyResponse = data;
      renderPharmacies(data);
    } catch (error) {
      if (elements.pharmacyOffers) {
        elements.pharmacyOffers.innerHTML = `<p class="empty">${error.message}</p>`;
      }
    }
  };

  const renderPharmacies = (data) => {
    const offers = data.offers || [];
    if (!elements.pharmacyOffers) return;
    if (offers.length === 0) {
      elements.pharmacyOffers.innerHTML = `<p class="empty">${t("ui.pharmacies.none", "No offers found for this medicine in the selected region.")}</p>`;
      return;
    }
    const currency = offers[0]?.currency;
    elements.pharmacyOffers.innerHTML = offers
      .map((offer) => {
        const distance = offer.distance_km != null ? `${offer.distance_km.toFixed(1)} km` : t("ui.pharmacies.delivery", "Delivery");
        const priceString = formatPrice(offer.price, offer.currency || currency);
        const deliveryLabel = t("ui.pharmacies.delivery", "Delivery");
        const updatedLabel = t("ui.pharmacies.last_updated", "Last updated");
        const viewSite = t("ui.pharmacies.view_site", "View site");
        return `
          <article class="offer-card">
            <header>
              <h3>${offer.partner}</h3>
              <span class="chip">${offer.type}</span>
            </header>
            <p class="offer-price">${priceString}</p>
            <p class="offer-meta">${offer.address}${offer.distance_km != null ? ` · ${distance}` : ""}</p>
            ${offer.delivery ? `<p class="offer-meta"><strong>${deliveryLabel}:</strong> ${offer.delivery}</p>` : ""}
            <p class="offer-meta"><strong>${updatedLabel}:</strong> ${offer.last_updated}</p>
            ${offer.url ? `<a class="offer-link" href="${offer.url}" target="_blank" rel="noopener">${viewSite}</a>` : ""}
          </article>`;
      })
      .join("");
  };

  const loadEducation = async () => {
    if (!elements.modulesContainer) return;
    try {
      const response = await fetch(`/api/education/modules?lang=${encodeURIComponent(state.lang)}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Unable to load education modules");
      }
      renderEducationModules(data.modules || []);
      if (data.advice && elements.adviceBanner && !state.lastSearchResponse) {
        elements.adviceBanner.textContent = data.advice;
      }
    } catch (error) {
      elements.modulesContainer.innerHTML = `<p class="empty">${error.message}</p>`;
    }
  };

  const renderEducationModules = (modules) => {
    if (!modules.length) {
      elements.modulesContainer.innerHTML = `<p class="empty">${t("ui.education.more", "Explore guidance")}</p>`;
      return;
    }
    elements.modulesContainer.innerHTML = modules
      .map((module) => {
        const tips = Array.isArray(module.tips)
          ? module.tips.map((tip) => `<li>${tip}</li>`).join("")
          : "";
        const featured = (module.featured_medicines || [])
          .map((med) => `<span class="chip chip--pill">${med}</span>`)
          .join(" ");
        return `
          <article class="module-card">
            <h3>${module.title}</h3>
            <p>${module.summary}</p>
            ${featured ? `<div class="module-meds">${featured}</div>` : ""}
            ${tips ? `<ul class="module-tips">${tips}</ul>` : ""}
          </article>`;
      })
      .join("");
  };

  const handleSavingsSubmit = async (event) => {
    event.preventDefault();
    const medicine = elements.savingsMedicine.value.trim();
    const months = Number(elements.savingsMonths.value) || 12;
    const quantity = Number(elements.savingsQuantity.value) || 1;
    if (!medicine) {
      elements.savingsOutput.textContent = t("ui.feedback.enter_more", "Enter at least two characters to search.");
      return;
    }
    try {
      const response = await fetch(`/api/education/savings?lang=${encodeURIComponent(state.lang)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ medicine, months, monthly_quantity: quantity }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Unable to compute savings");
      }
      const savingsLabel = t("ui.savings.result", "Estimated total savings");
      const advice = data.advice || state.latestAdvice || t("advice", "");
      elements.savingsOutput.innerHTML = `
        <p><strong>${savingsLabel}:</strong> ${formatPrice(data.total_savings, { symbol: "$", code: "" })}</p>
        <p>${advice}</p>`;
    } catch (error) {
      elements.savingsOutput.textContent = error.message;
    }
  };

  const runSearch = async (event) => {
    event.preventDefault();
    const query = elements.input.value.trim();
    if (query.length < 2) {
      elements.feedback.textContent = t("ui.feedback.enter_more", "Enter at least two characters to search.");
      elements.feedback.classList.remove("visually-hidden");
      return;
    }
    const params = new URLSearchParams({ q: query, lang: state.lang });
    const locality = elements.locality.value.trim();
    if (locality) {
      params.set("locality", locality);
    }
    elements.feedback.textContent = t("ui.feedback.searching", "Searching...");
    elements.feedback.classList.remove("visually-hidden");
    try {
      const response = await fetch(`/api/medicines?${params.toString()}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Unexpected error");
      }
      renderResults(data);
    } catch (error) {
      elements.feedback.textContent = error.message;
      elements.results.innerHTML = "";
    }
  };

  const changeLanguage = async (event) => {
    const lang = event.target.value || "en";
    if (lang === state.lang) return;
    state.lang = lang;
    await ensureTranslations();
    await loadEducation();
    if (state.selectedMedicine) {
      await fetchPharmacyOffers(state.selectedMedicine.brand_name);
    }
  };

  ensureTranslations().then(loadEducation);

  if (elements.form) {
    elements.form.addEventListener("submit", runSearch);
  }
  if (elements.languageSelect) {
    elements.languageSelect.addEventListener("change", changeLanguage);
  }
  if (elements.savingsForm) {
    elements.savingsForm.addEventListener("submit", handleSavingsSubmit);
  }
});
