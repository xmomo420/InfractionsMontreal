import os
import secrets
from functools import wraps

from flask import Flask, g, redirect, render_template, request, url_for, jsonify, url_for, session
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
    errors = [validation_error.message for validation_error in e.errors]
    message = ("Le formulaire n'a pas été rempli correctement, veuillez remplir tous les champs et respecter les "
               "critères")
    return jsonify({'error': e.message, 'errors': errors, 'message': message}), 400


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


# Gestion de la session en cours
def est_authentifie():
    if 'id' in session:
        id_session_db = get_db_utilisateurs().get_session(session['id'])
        return id_session_db is not None


def authentification_requise(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not est_authentifie():
            message = "Vous devez d'abord vous authentifier"
            return redirect(url_for('login', message=message), 302)
        return f(*args, **kwargs)
    return decorated


@app.route('/doc')
def doc():
    # TODO : Avec le fichier RAML et la commande
    return render_template('doc.html')


def courriel_unique(courriel) -> bool:
    liste_courriels = get_db_utilisateurs().get_all_courriels()
    return courriel not in liste_courriels


@app.route('/inscription', methods=['GET'])
def inscription():
    criteres_mdp = [
        "Doit contenir au moins 8 caractères au total",
        "Doit contenir au moins une lettre minuscule",
        "Doit contenir au moins une lettre majuscule",
        "Doit contenir au moins un chiffre",
        "Doit contenir au moins un caractère spécial"
    ]
    criteres = {
        "prenom": "Un prénom ne peut pas être vide",
        "nom": "Un nom ne peut pas être vide",
        "courriel": "Une adresse courriel valide est obligatoire",
        "confirmation_courriel": "Vous devez confirmer l'adresse courriel",
        "mot_de_passe": "Le mot de passe doit respecter les critères",
        "confirmation_mot_de_passe": "Les mots de passe ne correspondent pas ou ne sont pas valides",
    }
    dict_etablissements = get_db_infractions().get_all_etablissements()
    message = request.args.get('message', None)
    return render_template('inscription.html', nom_page='Inscription', criteres_mdp=criteres_mdp,
                           liste=dict_etablissements, criteres=criteres, message=message), 200


@app.route('/api/inscription/traitement', methods=['POST'])
@schema_utilisateur.validate(valider_nouvel_utilisateur)
def traitement_inscription():
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
            id_utilisateur = get_db_utilisateurs().ajouter_utilisateur(nouvel_utilisateur)
            _id = uuid.uuid4().hex
            get_db_utilisateurs().creer_session(_id=_id, id_utilisateur=id_utilisateur)
            session['id'] = _id
            session['id_utilisateur'] = id_utilisateur
            message = "Inscription réussi !"
            code = 201
        else:
            message = f"L'adresse courriel \"{courriel}\" est déjà utilisée"
            code = 200
        return jsonify({"message": message, "code": code}), code

    except Exception as e:
        return jsonify(error="Une erreur interne s'est produite. L'erreur a été "
                             "signalée à l'équipe de développement."), 500


@app.route('/profil', methods=['GET'])
@authentification_requise
def profil():
    utilisateur_connecte = get_db_utilisateurs().get_utilisateur(session['id_utilisateur'])
    prenom = utilisateur_connecte.prenom
    nom = utilisateur_connecte.nom
    courriel = utilisateur_connecte.courriel
    _id = utilisateur_connecte.id
    id_etablissements = utilisateur_connecte.etablissements
    #etablissements =
    photo = utilisateur_connecte.photo
    if photo is not None:
        photo_b64 = base64.b64encode(photo).decode('utf-8')
    else:  # Photo NULL dans la BD, donc on utilise la photo par défaut
        if os.path.exists('static/images/photo_par_defaut.png'):
            # Lire le contenu de l'image en binaire
            with open('static/images/photo_par_defaut.png', 'rb') as file:
                image_par_defaut = file.read()
            # Convertir l'image en base64
            photo_b64 = base64.b64encode(image_par_defaut).decode('utf-8')
        else:
            # Si le fichier n'existe pas, attribuer une valeur par défaut
            photo_b64 = None
    return render_template('profil.html', nom_page='Profil', id=_id, prenom=prenom, nom=nom,
                           courriel=courriel, photo=photo_b64, etablissements=id_etablissements), 200


@app.route('/login', methods=['GET'])
def login():
    # TODO
    return render_template('login.html', nom_page='Authentification'), 200


@app.route('/api/login/traitement', methods=['POST'])
def traitement_login():
    # TODO
    return


@app.route('/logout')
@authentification_requise
def logout():
    id_session = session['id']
    session.pop('id', None)
    session.pop('id_utilisateur', None)
    get_db_utilisateurs().supprimer_session(id_session)
    message_logout = "Vous avez été déconnecté avec succès"
    return redirect(url_for('home', message=message_logout),
                    302)
