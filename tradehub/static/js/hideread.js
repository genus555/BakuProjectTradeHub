const button = document.getElementById("hide-read-btn");

button?.addEventListener("click", function() {

    const hiding = button.dataset.hiding !== "true";

    document.querySelectorAll(".user-link").forEach(function (offer) {

        if (offer.dataset.read === "true") {

            offer.style.display = hiding ? "none" : "";

        }

    });

    button.dataset.hiding=hiding;
    button.textContent = hiding ? "Show All" : "Hide Read";

});