from flask import Flask, g, redirect, render_template, request, url_for, jsonify
import requests
from database import Database
from infractions import Infractions
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from io import StringIO
import csv

app = Flask(__name__, static_url_path="", static_folder="static")



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.route('/')
def home():
    try:
        infractions = get_db().get_infractions()
        if len(infractions) == 0:
            return 'Aucune infraction trouvée', 404
        else:
            return render_template('acceuil.html', infractions=infractions), 200
    except Exception as e:
        return f'Une erreur interne s\'est produite. L\'erreur a été signalée à l\'équipe de développement: {str(e)}', 500

# Cette route permet de recuperer les donnees du fichier csv et les insere dans la base de donnees  A1
@app.route('/api/infractions-csv-to-db')
def index():
    try:
        url = 'https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv'
        response = requests.get(url)
        response.raise_for_status()

        csv_data = response.content.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_data))

        for row in csv_reader:
            date = datetime.strptime(row['date'], '%Y%m%d').date()
            date_jugement = datetime.strptime(
                row['date_jugement'], '%Y%m%d').date()
            date_statut = datetime.strptime(
                row['date_statut'], '%Y%m%d').date()
            infraction = Infractions(None, row['id_poursuite'], row['business_id'], date, row['description'], row['adresse'], date_jugement,
                                        row['etablissement'], row['montant'], row['proprietaire'], row['ville'], row['statut'], date_statut, row['categorie'])
            get_db().creer_infraction(infraction)
            print('Insertion de l\'infraction')
        return 'La base de données a été mise à jour avec succès!', 201
    except Exception as e:
        return f'Une erreur interne s\'est produite. L\'erreur a été signalée à l\'équipe de développement: {str(e)}', 500



# Ce script permet de lancer le scheduler qui permet de mettre a jour la base de donnees chaque jour a minuit A3
scheduler = BackgroundScheduler()
scheduler.add_job(index, 'cron', hour=00, minute=00, second=00)
scheduler.start()
print("Scheduler started...")



# Cette route permet de rechercher les infractions dans la base de donnees selon le nom de l'etablissement, le proprietaire et la rue. Ensuit elle retourne les resultats dans un tableau dans une page web A2
@app.route('/api/recherche-infraction', methods=['POST'])
def recherche():
    try:
        nom_etablissement = request.form['nomEtablissement']
        proprietaire = request.form['proprietaire']
        rue = request.form['rue']

        infractions = get_db().recherche_infraction(nom_etablissement, proprietaire, rue)
        if nom_etablissement == '' or proprietaire == '' or rue == '':
            return 'Veuillez entrer un nom d\'établissement, un propriétaire ou une rue', 400
        if len(infractions) == 0:
            return 'Aucune infraction trouvée', 404
        return render_template('infraction.html', infractions=infractions), 200
    except Exception as e:
        return f'Une erreur interne s\'est produite. L\'erreur a été signalée à l\'équipe de développement: {str(e)}', 500


# Cette route permet de recuperer les infractions selon une periode donnee et retourne les resultats en format json A4
@app.route('/api/contraventions')
def contraventions():
    try:
        date_debut = request.args.get('du')
        date_fin = request.args.get('au')
        infractions = get_db().get_infraction_by_date(date_debut, date_fin)
        infractions_json = [infraction.__dict__ for infraction in infractions]
        if date_debut is None or date_fin is None:
            return 'Les dates de début et de fin de la période doivent être fournies.', 400
        if len(infractions_json) == 0:
            return 'Aucune contravention n\'a été trouvée pour la période donnée.', 404
        return jsonify(infractions_json), 200
    except Exception as e:
        return f'Une erreur interne s\'est produite. L\'erreur a été signalée à l\'équipe de développement: {str(e)}', 500

@app.route('/api/etablissement/<int:id_business>')
def etablissement(id_business):
    try:
        infractions = get_db().get_infraction_by_id_business(id_business)
        infractions_json = [infraction.__dict__ for infraction in infractions]
        if len(infractions_json) == 0:
            return 'Aucune infraction trouvée', 404
        else:
            return jsonify(infractions_json), 200
    except Exception as e:
        return f'Une erreur interne s\'est produite. L\'erreur a été signalée à l\'équipe de développement.: {str(e)}', 500


@app.route('/doc')
def doc():
    return render_template('doc.html'), 200