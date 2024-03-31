const MESSAGE_ERREUR_500 = "Erreur lors de la soumission du formulaire:";
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
        console.log(data.message);
        if (data.code === 201) {
            // TODO : Modifier le document : "Vous pouvez fermer cette page"
            window.location.href = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUXbmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXA%3D";
        } else {
            // TODO :
        }
    })
    .catch(error => {
            console.error(MESSAGE_ERREUR_500, error);
    });
}

document.addEventListener('submit', function (event) {
    mettreListeAJour(event);
});