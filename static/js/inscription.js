// Array de tuple (string, int) -> (etablissement, id_business)
let etablissementsSurveilles = [

];

function ajouterDansLaTable(nom, idBusiness) {
    let corpsTable = document.getElementById("corpsTable");
    let tr = document.createElement("tr");
    tr.setAttribute("id", idBusiness)
    let colonneNom = document.createElement("td");
    colonneNom.textContent = nom;
    let colonneId = document.createElement("td");
    colonneId.textContent = idBusiness;
    // Créer le bouton pour supprimer
    let boutonSuppression = document.createElement("button");
    boutonSuppression.textContent = "Supprimer";
    const appelFonction = "supprimerEtablissement(" + idBusiness + ")";
    boutonSuppression.setAttribute("onclick", appelFonction);
    boutonSuppression.setAttribute("type", "button");
    boutonSuppression.classList.add("btn", "btn-danger");
    let colonneBouton = document.createElement("td");
    colonneBouton.appendChild(boutonSuppression);
    tr.appendChild(colonneNom);
    tr.appendChild(colonneId);
    tr.appendChild(colonneBouton);
    corpsTable.appendChild(tr);
}

function ajouterEtablissement() {
    const etablissement = document.getElementById("listeEtablissements").value;
    const [nom, idBusiness] = etablissement.split(',')
    const idBusinessInt = parseInt(idBusiness, 10);
    // Vérifier si l'élément n'est pas déjà dans la liste (utiliser idBusiness)
    const existeDeja = etablissementsSurveilles.some(([_, id]) => id === idBusinessInt);
    if (idBusinessInt !== -1 && !existeDeja) {
        etablissementsSurveilles.push([nom, idBusinessInt]);
        ajouterDansLaTable(nom, idBusinessInt);
    }
}

function supprimerDansLaTable(idBusiness) {
    let rangee = document.getElementById(idBusiness);
    if (rangee)
        rangee.remove();
}

function supprimerEtablissement(idBusiness) {
    etablissementsSurveilles = etablissementsSurveilles.filter(([_, id]) => id !== idBusiness);
    supprimerDansLaTable(idBusiness);
}


document.querySelector('#boutonSoumission').addEventListener('click', function(event) {
    soumissionFormulaire(event);
});

function soumissionFormulaire(event) {
    event.preventDefault();
    let formulaire = {
        prenom: document.getElementById("prenom").value,
        nom: document.getElementById("nom").value,
        courriel: document.getElementById("courriel").value,
        mot_de_passe: document.getElementById("motDePasse").value,
        etablissements: etablissementsSurveilles.map(([_, idBusiness]) => idBusiness)
    };

        // Envoyer les données du formulaire au backend en tant qu'objet JSON
        fetch('/api/inscription/traitement', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formulaire)
        })
        .then(response => response.json())
        .then(data => {
            // Traiter la réponse du backend
            if (data.code === 201) {
                console.log(data.message);
                window.location.href = url; // Redirection vers la page d'accueil
            } else {
                // TODO : Si l'inscription n'a pas pu se faire
                // TODO : Bonus : Ajouter la classe 'is-invalid' ou 'is-valid' aux <input> valides/invalides
                console.error(data.errors);
                let message = document.getElementById("message");
                message.innerText = data.message;
                let conteneurMessage = document.getElementById("conteneurMessage");
                conteneurMessage.style.display = "block";
            }
        })
        .catch(error => {
            console.error('Erreur lors de la soumission du formulaire:', error);
        });
}