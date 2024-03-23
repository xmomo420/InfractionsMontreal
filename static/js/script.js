console.log('Script chargé !');

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

