// Array de tuple (string, int) -> (etablissement, id_business)
let etablissementsSurveilles = [

];

const MESSAGE_ERREUR_500 = "Erreur lors de la soumission du formulaire:";

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

/**
 * Cette fonction est utilisée dans à l'aide des <button> 'Supprimer' qui sont ajoutés dans
 * la fonction 'ajouterDansLaTable()'
 * @param idBusiness l'id du business de l'établissement
 */
function supprimerEtablissement(idBusiness) {
    etablissementsSurveilles = etablissementsSurveilles.filter(([_, id]) => id !== idBusiness);
    supprimerDansLaTable(idBusiness);
}

const formulaireLogin = document.getElementById("formulaireLogin");
if (formulaireLogin != null)
    formulaireLogin.addEventListener('submit', function (event) {
       soumissionLogin(event);
    });

function soumissionLogin(event) {
    event.preventDefault();
    let formulaire = {
        courriel: document.getElementById("courriel").value,
        mot_de_passe: document.getElementById("motDePasse").value
    };

    // Envoyer les données à l'API
    fetch(urlApiLogin, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formulaire)
    })
        .then(response => response.json())
        .then(data => {
            // TODO : Gérer la gestion du formulaire
            if (data == null) // Champs valides et l'utilisateur est authentifié
                window.location.href = urlHome;
            else  { // Champs valides mais le mot de passe ou courriel sont erronés
                let message = document.getElementById("message");
                message.innerText = data.message;
                let conteneurMessage = document.getElementById("conteneurMessage");
                conteneurMessage.style.display = "block";
            }
        })
        .catch(error => {
            console.error(MESSAGE_ERREUR_500, error)
        })
}

const formulaireInscription = document.getElementById("formulaireInscription");
if (formulaireInscription != null)
    formulaireInscription.addEventListener('submit', function (event) {
        soumissionInscription(event);
    });

function soumissionInscription(event) {
    event.preventDefault();
    let formulaire = {
        prenom: document.getElementById("prenom").value,
        nom: document.getElementById("nom").value,
        courriel: document.getElementById("courriel").value,
        mot_de_passe: document.getElementById("motDePasse").value,
        etablissements: etablissementsSurveilles.map(([_, idBusiness]) => idBusiness)
    };

    // Envoyer les données du formulaire au backend en tant qu'objet JSON
    fetch(urlApiInscription, {
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
                window.location.href = urlHome; // Redirection vers la page d'accueil
            } else { // Si l'inscription n'a pas pu se faire
                // TODO : Bonus : Ajouter la classe 'is-invalid' ou 'is-valid' aux <input> valides/invalides
                console.error(data.errors);
                let message = document.getElementById("message");
                message.innerText = data.message;
                let conteneurMessage = document.getElementById("conteneurMessage");
                conteneurMessage.style.display = "block";
            }
        })
        .catch(error => {
            console.error(MESSAGE_ERREUR_500, error);
        });
}

document.addEventListener("DOMContentLoaded", function() {
    if (document.getElementById("formulaireModifications") != null)
        initialiserListe();
});

function initialiserListe() {
    const tbody = document.getElementById("corpsTable");
    const rangees = tbody.querySelectorAll("tr");
    rangees.forEach(
        rangee => {
            const colonnes = rangee.querySelectorAll("td");
            const nom = colonnes[0].textContent;
            const idBusiness = colonnes[1].textContent;
            const idBusinessInt = parseInt(idBusiness, 10);
            etablissementsSurveilles.push([nom, idBusinessInt]);
        }
    );
}

const formulaireModifications = document.getElementById("formulaireModifications");
if (formulaireModifications != null)
    formulaireModifications.addEventListener('submit', function (event) {
       soumissionModifications(event);
    });

function soumissionModifications(event) {
    event.preventDefault();
    let formulaire = document.getElementById("formulaireModifications");
    const donnees = new FormData(formulaire);
    const listeJson = JSON.stringify(etablissementsSurveilles.map(([_, idBusiness]) => idBusiness));
    donnees.append("liste_etablissements", listeJson);
    fetch(urlApiModifications, {
        method: 'PUT',
        body: donnees
    })
        .then(response => response.json())
        .then(data => {
            // Faire défiler la page vers le haut
            window.scrollTo(0, 0);
            let conteneurMessage = document.getElementById("conteneurMessage");
            conteneurMessage.style.display = "block";
            let message = document.getElementById("contenuMessage");
            message.innerText = data.message;
             if (data.code === 200) {
                 conteneurMessage.classList.remove("alert-danger");
                 conteneurMessage.classList.add("alert-success");
                 if (data.photo) {
                     let champNouvellePhoto = document.getElementById("photoActuelle");
                     // Créer un objet FileReader
                     let reader = new FileReader();
                     // Définir une fonction de rappel pour lorsque la lecture du fichier est terminée
                     reader.onload = function(event) {
                         // Définir l'attribut src de l'élément image avec le contenu lu du fichier
                         champNouvellePhoto.setAttribute("src", event.target.result);
                     };
                     // Lire le contenu du fichier
                     reader.readAsDataURL(donnees.get("photo"));
                 }
             } else
                 console.error(data.errors);
        })
        .catch(error => {
            console.error(MESSAGE_ERREUR_500, error);
        });
}