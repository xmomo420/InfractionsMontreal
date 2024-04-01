const MESSAGE_ERREUR_500 = "Erreur lors de la soumission du formulaire:";
const MESSAGE_SUPPRESSION_REUSSI = "Votre profil a été mis-à-jour correctement\nVous pouvez fermer cette page";
function mettreListeAJour(event) {
    event.preventDefault();
    const formulaire = {
        etablissement: parseInt(document.getElementById("etablissement").value, 10),
        id_utilisateur: parseInt(document.getElementById("id_utilisateur").value, 10),
        token: document.getElementById("token").value
    };
    fetch(urlApiSuppression, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formulaire)
    })
    .then(response => response.json())
    .then(data => {
        let conteneurMessage = document.getElementById("conteneurMessage");
        let contenuMessage = document.getElementById("contenuMessage");
        let conteneurPage = document.getElementById("conteneurPage");
        conteneurMessage.style.display = "block";
        if (data.code === 201) {
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