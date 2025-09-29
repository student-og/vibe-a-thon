document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("search-form");
  const input = document.getElementById("search-input");
  const resultsContainer = document.getElementById("results");
  const feedback = document.getElementById("search-feedback");

  const renderResults = (data) => {
    if (!data.results || data.results.length === 0) {
      resultsContainer.innerHTML = `
        <div class="result-card">
          <p>No matches found. Try searching for another brand or generic name.</p>
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
          </article>`;
      })
      .join("");

    resultsContainer.innerHTML = html;
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = input.value.trim();
    if (query.length < 2) {
      feedback.textContent = "Enter at least two characters to search.";
      feedback.classList.remove("visually-hidden");
      return;
    }

    feedback.textContent = "Searching...";
    feedback.classList.remove("visually-hidden");

    try {
      const response = await fetch(`/api/medicines?q=${encodeURIComponent(query)}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Unexpected error");
      }

      feedback.textContent = data.count === 1 ? "1 match found." : `${data.count} matches found.`;
      renderResults(data);
    } catch (error) {
      feedback.textContent = error.message;
      resultsContainer.innerHTML = "";
    }
  });
});
