const offerForm = document.getElementById("offer-form")

offerForm.addEventListener("submit", function(event) {

    const offered = document.querySelectorAll("input[name='offered_bakugan']");
    const price = document.querySelector("input[name='offered_price']").value;

    if (offered.length === 0 && Number(price) === 0) {
        event.preventDefault();
        alert("Trade offer can't be empty. Make new trade or add HSP/Bakugan.")
    }

});