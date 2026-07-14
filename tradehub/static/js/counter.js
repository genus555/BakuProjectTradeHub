const editingElement = document.getElementById("edited");
let edited = editingElement.dataset.edited === "true";

console.log(editingElement.dataset.edited);
console.log(edited);

const acceptButton = document.getElementById("accept-btn");
const counterButton = document.getElementById("counter-btn");

document.querySelectorAll(".offer-btn").forEach(button => {
    button.addEventListener("click", () => {
        showUpdate();
    });
});

document.querySelectorAll("input[type='number']").forEach(input => {
    input.addEventListener("change", () => {
        showUpdate();
    });
});

function showUpdate() {
    acceptButton.style.display = "none";
    counterButton.style.display = "block";
}