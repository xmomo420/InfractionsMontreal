$(document).ready(function() {
    $('#button-recherche').on('click', function(event) {

        var dateDebut = $('#date-debut').val();
        var dateFin = $('#date-fin').val();

        fetch('/api/contraventions?du=' + dateDebut + '&au=' + dateFin)
        .then(response => response.json())
        .then(data => {
            // Créer un objet pour compter les occurrences de chaque restaurant
            var counts = {};
            data.forEach(item => {
                if (counts[item.etablissement]) {
                    counts[item.etablissement]++;
                } else {
                    counts[item.etablissement] = 1;
                }
            });

            // Créer le tableau HTML
            var html = '<table><tr class="text-center"><th>Etablissement</th><th>Occurrences</th><th>Action</th></tr>';
            if (Object.keys(counts).length === 0) {
                html += '<tr><td colspan="2">Aucun résultat</td></tr>';
            }
            for (var etablissement in counts) {
                html += '<tr><td>' + etablissement + '</td><td>' + counts[etablissement] + '</td><td><button id="button-modifier" class="btn btn-outline-primary mt-3">Modifier</button></td><td><button id="button-supprimer" class="btn btn-outline-primary mt-3">Supprimer</button></td></tr>';
            }
            html += '</table>';
            $('#resultat-recherche').html(html);
        })
        .catch(error => {
            console.error('Erreur avec le serveur :', error);
        });
    });
});

$(document).on('click', '#button-modifier', function(event) {
    var etablissement = $(this).closest('tr').find('td:first').text();
    console.log(etablissement);
});

$(document).on('click', '#button-supprimer', function(event) {
    var etablissement = $(this).closest('tr').find('td:first').text();
    var encodedEtablissement = encodeURIComponent(etablissement);

    fetch('/api/supprimer-etablissement/' + etablissement, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        var userResponse = confirm('L\'établissement a été supprimé avec succès.');
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
                    var html = '<table><tr><th>Poursuite(ID)</th><th>Business(ID)</th><th>Date</th><th>Description</th><th>Adresse</th><th>Date jugement</th><th>Etablissement</th><th>Montant</th><th>Proprietaire</th><th>Ville</th><th>Statut</th><th>Date statut</th><th>Categorie</th></tr>'
                    data.forEach(infraction => {
                        html += '<tr> <td>' + infraction.id_poursuite + '</td> <td>' + infraction.id_business + '</td> <td>' + infraction.date + '</td> <td>' + infraction.description + '</td> <td>' + infraction.adresse + '</td> <td>' + infraction.date_jugement + '</td> <td>' + infraction.etablissement + '</td> <td>' + infraction.montant + '</td> <td>' + infraction.proprietaire + '</td> <td>' + infraction.ville + '</td> <td>' + infraction.statut + '</td> <td>' + infraction.date_statut + '</td> <td>' + infraction.categorie + '</td> </tr>';
                    });
                    html += '</table>';

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


