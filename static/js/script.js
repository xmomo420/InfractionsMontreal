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
            var html = '<table><tr><th>Etablissement</th><th>Occurrences</th></tr>';
            if (Object.keys(counts).length === 0) {
                html += '<tr><td colspan="2">Aucun résultat</td></tr>';
            }
            for (var etablissement in counts) {
                html += '<tr><td>' + etablissement + '</td><td>' + counts[etablissement] + '</td></tr>';
            }
            html += '</table>';
            $('#resultat-recherche').html(html);
        })
        .catch(error => {
            console.error('Erreur avec le serveur :', error);
        });
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

        fetch('/api/demande-inspections', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(json)

        })
        .then(response => response.json())
        .then(data => {
            if (data) {
                console.log(data.message);
                $('#message').html('Demande envoyée avec succès');
                $('#message').addClass('alert alert-success');
            }else{
                $('#message').html('Erreur lors de l\'envoi de la demande');
                $('#message').addClass('alert alert-danger');
            }

        })
        .catch(error => {
            console.error('Erreur :', error);
        });
    });
});


