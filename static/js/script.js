$(document).ready(function() {
    $('#button-recherche').on('click', function(event) {

        let dateDebut = $('#date-debut').val();
        let dateFin = $('#date-fin').val();



        fetch('/api/contraventions?du=' + dateDebut + '&au=' + dateFin)
        .then(response => response.json())
        .then(data => {
            // Créer un objet pour compter les occurrences de chaque restaurant
            let counts = {};
            data.forEach(item => {
                if (counts[item.etablissement]) {
                    counts[item.etablissement]++;
                } else {
                    counts[item.etablissement] = 1;
                }
            });

            // Créer le tableau HTML
            let html = '<table class="table align-middle table-secondary table-bordered">' +
                                '<thead class="table-primary">' +
                                    '<tr>' +
                                        '<th scope="col">Etablissement</th>' +
                                        '<th scope="col">Occurrences</th>' +
                                        '<th scope="col"></th>' +
                                    '</tr>' +
                                '</thead>' +
                                '<tbody>';
            if (Object.keys(counts).length === 0) {
                html += '<tr>' +
                            '<td colspan="3">Aucun résultat</td>' +
                        '</tr>';
            }
            for (let etablissement in counts) {
                html += '<tr>' +
                            '<td>' + etablissement + '</td>' +
                            '<td>' + counts[etablissement] + '</td>' +
                            '<td>' +
                                '<div class="d-flex text-start">' +
                                    '<button id="button-modifier" class="btn btn-sm btn-success mx-1">Modifier</button>' +
                                    '<button id="button-supprimer" class="btn btn-sm btn-danger">Supprimer</button>' +
                                '</div>' +
                            '</td>' +
                        '</tr>';
            }
            html += '</tbody></table>';
            $('#resultat-recherche').html(html);
        })
        .catch(error => {
            console.error('Erreur avec le serveur :', error);
        });
    });
});

$(document).on('click', '#button-modifier', function(event) {
    let etablissement = $(this).closest('tr').find('td:first').text();
    let encodedEtablissement = encodeURIComponent(etablissement);

    fetch('/modifier-etablissement/' + etablissement, {
        method: 'GET',
        redirect: 'follow',
    })
    .then(response => response.text())
    .then(data => {
        window.location.href = '/modifier-etablissement/' + encodedEtablissement;
    })
    .catch(error => console.error('Erreur :', error));
});

$(document).on('click', '#button-modification-etablissement', async function(event) {

    let inputElement = document.getElementById('nom-etablissement');
    let nomEtablissement = inputElement.getAttribute('placeholder');

    try {
        let response = await fetch('/modifier-etablissement/' + nomEtablissement, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nom_etablissement: $('#nom-etablissement').val(),
            })
        });

        let data = await response.json();

        console.log('Réponse :', data);
        let userResponse = confirm('L\'établissement a été modifié avec succès.');
        if (userResponse) {
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Erreur :', error);
    }
    });

$(document).on('click', '#button-supprimer', function(event) {
    let etablissement = $(this).closest('tr').find('td:first').text();
    let encodedEtablissement = encodeURIComponent(etablissement);

    let token = window.btoa('admin:admin');
        let authToken = 'Basic ' + token;

        let headers = new Headers();
        headers.append('Authorization', authToken);

    fetch('/api/retirer-etablissement/' + encodedEtablissement, {
        method: 'DELETE',
        headers: headers
    })
    .then(response => response.json())
    .then(data => {
        let userResponse = confirm('L\'établissement a été supprimé avec succès.');
        if (userResponse) {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Erreur avec le serveur :', error);
    });
});


$(document).ready(function() {
    $('#champ-etablissements').change(function() {
        const etablissement = $(this).val();  // Obtient la valeur du champ de sélection

        if (etablissement) {  // Si un établissement a été sélectionné
            fetch('/api/etablissement/' + etablissement)  // Envoie une requête GET à l'API
                .then(response => response.json())  // Convertit la réponse en objet JavaScript
                .then(data => {
                    // Crée le tableau HTML
                    let html =
                               '<h5 class="mb-3 text-start">Renseignements</h5>' +
                               '<div class="table-responsive text-center">' +
                                   '<table class="table align-middle table-success table-bordered">' +
                                       '<thead class="table-warning">' +
                                           '<tr>' +
                                               '<th scope="col">Propriétaire</th>' +
                                               '<th scope="col">Adresse</th>' +
                                               '<th scope="col">Ville</th>' +
                                           '</tr>' +
                                       '</thead>' +
                                       '<tbody>' +
                                           '<tr>' +
                                               '<td>' + data["proprietaire"] + '</td>' +
                                               '<td>' + data.adresse.substring(0, data.adresse.indexOf(',')) + '</td>' +
                                               '<td>' + data.ville + '</td>' +
                                           '</tr>' +
                                       '</tbody>' +
                                   '</table>' +
                               '</div>' +
                               '<h5 class="text-start mb-3">Infraction(s) :<h5/>';
                    data["infractions"].forEach((infraction, index) => {
                        console.log(index);
                        html += '<div class="g-3">' +
                                    '<h6 class="text-start">Description</h6>' +
                                    '<p class="fw-normal" style="font-size: small; text-align: justify">' + infraction.description + '</p>' +
                                    '<div style="font-size: medium" class="fw-normal table-responsive text-center">' +
                                        '<table class="table align-middle table-secondary table-bordered">' +
                                            '<thead class="table-primary">' +
                                            '<tr>' +
                                                    '<th scope="col">Date</th>' +
                                                    '<th scope="col">Date jugement</th>' +
                                                    '<th scope="col">Montant</th>' +
                                                    '<th scope="col">Statut</th>' +
                                                    '<th scope="col">Date Statut</th>' +
                                                    '<th scope="col">Catégorie</th>' +
                                                '</tr>' +
                                            '</thead>' +
                                            '<tbody>' +
                                                '<tr>' +
                                                    '<td>' + infraction.date + '</td>' +
                                                    '<td>' + infraction.date_jugement + '</td>' +
                                                    '<td>' + infraction.montant + ' $</td>' +
                                                    '<td>' + infraction.statut + '</td>' +
                                                    '<td>' + infraction.date_statut + '</td>' +
                                                    '<td>' + infraction.categorie + '</td>' +
                                                '</tr>' +
                                            '</tbody>' +
                                        '</table>' +
                                    '</div>' +
                                    (index !== data["infractions"].length - 1 ? '<hr class="bg-primary border border-dark border-2 card">' : '') +
                                '</div>';
                    });
                    // Met à jour le contenu du tableau
                    $('#tableau-etablissement').html(html);
                })
                .catch(error => {
                    // Gère les erreurs
                    console.error('Erreur :', error);
                });
        } else {
            // Si aucun établissement n'a été sélectionné, efface le tableau
            $('#tableau-etablissement').html('');
        }
    });
});

$(document).ready(function() {
    $('#formulairePlainte').on('submit', function(event) {
        event.preventDefault();
        let etablissement = $('#etablissement').val();
        let adresse = $('#adresse').val();
        let ville = $('#ville').val();
        let date_visite = $('#date_visite_client').val();
        let nom = $('#nom_client').val();
        let prenom = $('#prenom_client').val();
        let description = $('#description_probleme').val();

        let json = {
            etablissement: etablissement,
            adresse: adresse,
            ville: ville,
            date_visite_client: date_visite,
            nom_client: nom,
            prenom_client: prenom,
            description_probleme: description
        }

        fetch('/api/demande-inspection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(json)

        })
        .then(response => response.json())
        .then(data => {
            if (data) {
                $('#message').html('Demande envoyée avec succès');
                $('#message').addClass('alert alert-success');
                // Réinitialiser les champs du formulaire
                $('#etablissement').val('');
                $('#adresse').val('');
                $('#ville').val('');
                $('#date_visite_client').val('');
                $('#nom_client').val('');
                $('#prenom_client').val('');
                $('#description_probleme').val('');
            } else {
                $('#message').html('Erreur lors de l\'envoi de la demande');
                $('#message').addClass('alert alert-danger');
            }

        })
        .catch(error => {
            console.error('Erreur :', error);
        });
    });
});


