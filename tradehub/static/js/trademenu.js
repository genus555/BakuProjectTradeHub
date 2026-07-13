document.querySelectorAll(".offer-btn").forEach(button => {
    
    button.addEventListener("click", function() {
        
        const card = this.closest(".inv-card");
        const id = this.dataset.id;
        const input = document.getElementById(`offer-input-${id}`);

        if (input) {
            input.remove();
        }

        if (card) {
            card.remove()
        }

    });

});