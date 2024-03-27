import secrets

from flask import Flask, g, redirect, render_template, request, url_for, jsonify, url_for
import requests
from schema_utilisateur import valider_nouvel_utilisateur
from flask_json_schema import JsonValidationError, JsonSchema
from database_infractions import DatabaseInfractions
from database_utilisateur import DatabaseUtilisateur
from infractions import Infractions
from utilisateur import Utilisateur
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from io import StringIO
import base64
import hashlib
import uuid
import csv

app = Flask(__name__, static_url_path="", static_folder="static")
schema_utilisateur = JsonSchema(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)


@app.errorhandler(JsonValidationError)
def validation_error(e):
    errors = [validation_error.message for _validation_error in e.errors]
    return jsonify({'error': e.message, 'errors': errors}), 400


def get_db_infractions():
    db = getattr(g, '_database_infractions', None)
    if db is None:
        g._database_infractions = DatabaseInfractions()
    return g._database_infractions


def get_db_utilisateurs():
    db = getattr(g, '_database_utilisateurs', None)
    if db is None:
        g._database_utilisateurs = DatabaseUtilisateur()
    return g._database_utilisateurs


@app.teardown_appcontext
def close_connection(exception):
    db_infractions = getattr(g, '_database_infractions', None)
    if db_infractions is not None:
        db_infractions.disconnect()


@app.route('/')
def home():
    return render_template('accueil.html', nom_page='Infractions Montréal'), 200


# Cette route permet de recuperer les donnees du fichier csv et les insere dans la base de donnees  A1
@app.route('/api/infractions-csv-to-db')
def index():
    with app.app_context():  # Envelopper le code dans un contexte d'application Flask
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
            infraction = Infractions(None, row['id_poursuite'], row['business_id'], date, row['description'],
                                     row['adresse'], date_jugement,
                                     row['etablissement'], row['montant'], row['proprietaire'], row['ville'],
                                     row['statut'], date_statut, row['categorie'])
            get_db_infractions().creer_infraction(infraction)
            print('Insertion de l\'infraction')
        return 'La base de données a été mise à jour avec succès!', 201


# Ce script permet de lancer le scheduler qui permet de mettre a jour la base de donnees chaque jour a minuit A3
scheduler = BackgroundScheduler()
scheduler.add_job(index, 'cron', hour=00, minute=00, second=00)
scheduler.start()
print("Scheduler started...")


# Cette route permet de rechercher les infractions dans la base de donnees selon le nom de l'etablissement,
# le proprietaire et la rue. Ensuit elle retourne les resultats dans un tableau dans une page web A2
@app.route('/api/recherche-infraction', methods=['POST'])
def recherche():
    nom_etablissement = request.form['nomEtablissement']
    proprietaire = request.form['proprietaire']
    rue = request.form['rue']

    infractions = get_db_infractions().recherche_infraction(nom_etablissement, proprietaire, rue)
    return render_template('infraction.html', infractions=infractions), 200


# Cette route permet de recuperer les infractions selon une periode donnee et retourne les resultats en format json A4
@app.route('/api/contraventions')
def contraventions():
    date_debut = request.args.get('du')
    date_fin = request.args.get('au')
    infractions = get_db_infractions().get_infraction_by_date(date_debut, date_fin)
    infractions_json = [infraction.__dict__ for infraction in infractions]
    return jsonify(infractions_json), 200


@app.route('/etablissements')
def etablissements():
    infractions = get_db_infractions().get_infractions()
    return render_template('etablissements.html', infractions=infractions), 200


@app.route('/api/etablissement/<int:id_business>')
def etablissement(id_business):
    infractions = get_db_infractions().get_infraction_by_id_business(id_business)
    infractions_json = [infraction.__dict__ for infraction in infractions]
    return jsonify(infractions_json), 200


@app.route('/doc')
def doc():
    return render_template('doc.html')


def courriel_unique(courriel):
    liste_courriels = get_db_utilisateurs().get_all_courriels()
    return courriel in liste_courriels


@app.route('/api/inscription', methods=['POST'])
@schema_utilisateur.validate(valider_nouvel_utilisateur)
def inscription():
    try:
        data = request.get_json()
        prenom = data.get("prenom")
        nom = data.get("nom")
        courriel = data.get("courriel")
        mot_de_passe = data.get("mot_de_passe")
        _etablissements = data.get("etablissements")
        if courriel_unique(courriel):
            salt = uuid.uuid4().hex
            hashed = hashlib.sha512(str(mot_de_passe + salt).encode("utf-8")).hexdigest()
            nouvel_utilisateur = Utilisateur(_id=None, prenom=prenom.strip(), nom=nom.strip(),
                                             courriel=courriel.strip(), salt=salt, _hash=hashed, photo=None,
                                             etablissements=_etablissements)
            get_db_utilisateurs().ajouter_utilisateur(nouvel_utilisateur)
            message = "Inscription réussi !"
            code = 201
        else:
            message = f"L'adresse courriel \"{courriel}\" est déjà utilisée"
            code = 200
        return message, code

    except Exception as e:
        return jsonify(error="Une erreur interne s'est produite. L'erreur a été "
                             "signalée à l'équipe de développement."), 500
