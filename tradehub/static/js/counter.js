let edited = false;

const acceptButton = document.getElementById("accept-btn")
const counterButton = document.getElementById("counter-btn")

document.querySelectorAll(".offer-btn").forEach(button => {

    button.addEventListener("click", function() {

        edited = true;
        acceptButton.style.display = "none";
        counterButton.style.display = "block";

    });

});

document.querySelectorAll("input[type='number']").forEach(input => {

    input.addEventListener("change", () => {

        edited = true;
        acceptButton.style.display = "none";
        counterButton.style.display = "block";

    });

});