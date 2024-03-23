console.log('Script chargé !');

$(document).ready(function() {
    $('#button-recherche').on('click', function(event) {

        var dateDebut = $('#date-debut').val();
        var dateFin = $('#date-fin').val();

        fetch('/api/contraventions?du=' + dateDebut + '&au=' + dateFin)
            .then(response => response.text())
            .then(data => {
                $('#resultat-recherche').html(data);
            })
            .catch(error => {
                console.error('Erreur avec le serveur :', error);
            })
    });
});

