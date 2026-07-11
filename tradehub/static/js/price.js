console.log("price.js loaded");
document.querySelectorAll('[name="trade_type"]').forEach(select => {
    select.addEventListener("change", function() {
        const form = this.closest("form");
        const priceContainer = form.querySelector(".price-container");
        const priceInput = form.querySelector(".price-input");

        if (this.value === "selling" || this.value === "both") {
            priceContainer.style.display = "block";
            priceInput.required = true;
        } else {
            priceContainer.style.display = "none";
            priceInput.required = false;
            priceInput.value = '';
        }
    });
});