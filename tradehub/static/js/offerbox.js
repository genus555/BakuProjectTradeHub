const inventoryGrid = document.getElementById("inventory-grid");
const offerGrid = document.getElementById("offer-grid");
const form = document.querySelector(".offering-container form");

document.querySelectorAll(".offer-btn").forEach(button => {

    button.addEventListener("click", function() {

        const card = this.closest(".inv-card");
        const id = this.dataset.id;

        if (card.parentElement === inventoryGrid) {

            offerGrid.appendChild(card);
            this.textContent = "Remove from Offer";

            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "offered_bakugan";
            input.value = id;
            input.id = `offer-input-${id}`;

            form.appendChild(input);

        } else {

            inventoryGrid.appendChild(card);
            this.textContent = "Add to Offer";

            document.getElementById(`offer-input-${id}`).remove();

        }

    });

});