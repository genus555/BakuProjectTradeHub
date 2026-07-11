const tradeType = document.querySelector("select[name='trade_type']");
const priceContainer = document.querySelector(".price-container");

function updatePriceVisibility() {
    if (tradeType.value === "selling" || tradeType.value === "both") {
        priceContainer.style.display = "block";
    } else {
        priceContainer.style.display = "none";
    }
}

tradeType.addEventListener("change", updatePriceVisibility);

updatePriceVisibility();