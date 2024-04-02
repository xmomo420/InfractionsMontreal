const MESSAGE_ERREUR_500 = "Erreur lors de la soumission du formulaire:";
const MESSAGE_SUPPRESSION_REUSSI = "Votre profil a été mis-à-jour correctement\nVous pouvez fermer cette page";
function mettreListeAJour(event) {
    event.preventDefault();
    fetch(urlApiSuppression, {
        method: 'PATCH',
    })
    .then(response => response.json())
    .then(data => {
        let conteneurMessage = document.getElementById("conteneurMessage");
        let contenuMessage = document.getElementById("contenuMessage");
        let conteneurPage = document.getElementById("conteneurPage");
        conteneurMessage.style.display = "block";
        if (data.code === 200) {
            contenuMessage.innerText = MESSAGE_SUPPRESSION_REUSSI;
            conteneurPage.style.display = "none";
        } else {
            conteneurMessage.classList.remove("alert-success");
            conteneurMessage.classList.add("alert-danger");
            contenuMessage.innerText = data.message;
        }
    })
    .catch(error => {
            console.error(MESSAGE_ERREUR_500, error);
    });
}

document.addEventListener('submit', function (event) {
    mettreListeAJour(event);
});