import base64
import csv
import hashlib
import io
import json
import os
import secrets
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from functools import wraps
from io import StringIO
from typing import List
from urllib.parse import unquote
import requests
import tweepy
import werkzeug.datastructures
from apscheduler.schedulers.background import BackgroundScheduler
from flask import (Flask, g, redirect, render_template, request, url_for,
                   jsonify, session, abort, make_response)
from flask_json_schema import JsonValidationError, JsonSchema
from flask_mail import Mail, Message
from database_infractions import DatabaseInfractions
from database_utilisateur import DatabaseUtilisateur
from demande_inspection import Inspection
from infractions import Infractions
from schema_inspection import inspection_schema
from schema_utilisateur import valider_nouvel_utilisateur, valider_login
from utilisateur import Utilisateur

app = Flask(__name__, static_url_path="", static_folder="static")
schema_utilisateur = JsonSchema(app)
schema_inspection = JsonSchema(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('ADRESSE_COURRIEL_EXPEDITEUR')
app.config['MAIL_PASSWORD'] = os.getenv('MOT_DE_PASSE_EXPEDITEUR')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DESTINATAIRE_CORRECTION'] = os.getenv(
    'ADRESSE_COURRIEL_DESTINATAIRE')
app.config['CLIENT_TWITTER'] = tweepy.Client(os.getenv('TWITTER_BEARER_TOKEN'),
                                             os.getenv('TWITTER_API_KEY'),
                                             os.getenv('TWITTER_API_SECRET'),
                                             os.getenv('TWITTER_ACCESS_TOKEN'),
                                             os.getenv(
                                                 'TWITTER_ACCESS_TOKEN_SECRET')
                                             )
mail = Mail(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)

MESSAGE_ERREUR_500 = ('Une erreur interne s\'est produite. L\'erreur a été '
                      'signalée à l\'équipe de développement')
MESSAGE_ERREUR_403 = "L'accès à cette ressource ne vous est pas autorisé"
MESSAGE_ERREUR_404 = ("La ressource à laquelle vous avez tenté d'accéder "
                      "n'existe pas")
MESSAGE_ERREUR_405 = ("La méthode que vous avez utilisée n'est pas permise "
                      "pour cet URL")


@app.route('/favicon.ico', methods=["GET"])
def favicon():
    return app.send_static_file('images/favicon.ico')


@app.errorhandler(JsonValidationError)
def validation_error(e):
    errors = [validation_error.message for validation_error in e.errors]
    message = "Un ou plusieurs champs sont invalide dans la requête"
    return (
        jsonify({'error': e.message, 'errors': errors, 'message': message}),
        400)


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
    try:
        infractions = get_db_infractions().get_infractions()
        etalissements = get_db_infractions().get_all_etablissements()
        if len(infractions) == 0:
            return redirect(url_for('index')), 302
        else:
            return render_template('accueil.html',
                                   message_logout=request.args.get(
                                       'message_logout', None),
                                   nom_page='Infractions Montréal',
                                   infractions=infractions,
                                   etalissements=etalissements), 200
    except Exception as e:
        return f'{MESSAGE_ERREUR_500} : {str(e)}', 500


def envoyer_courriel(infractions: List[Infractions]):
    objet = "Nouvelle(s) infraction(s) détectée(s)"
    sender = app.config['MAIL_USERNAME']
    destinataire = app.config['DESTINATAIRE_CORRECTION']
    nom_complet = get_db_utilisateurs().get_nom_by_courriel(destinataire)
    message = Message(subject=objet, sender=sender, recipients=[destinataire])
    message.html = render_template('courriels/courriel_infractions.html',
                                   nom_complet=nom_complet,
                                   infractions=infractions)
    mail.send(message)


def publier_tweet(infraction: Infractions):
    contenu_tweet = (f"Nouvelle infraction :\n"
                     f"{infraction.etablissement}, {infraction.adresse}, "
                     f"{infraction.date} : {infraction.montant} $")
    app.config['CLIENT_TWITTER'].create_tweet(text=contenu_tweet)


@app.route('/api/infractions-csv-to-db')
def index():
    # Pour gérer le problème des connections simultanées dans la BD
    # Envelopper le code dans un contexte d'application Flask
    with (app.app_context()):
        try:
            url = ('https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9'
                   '-5955efeb91a0/resource/7f939a08-be8a-45e1'
                   '-b208-d8744dca8fc6/download/violations.csv')
            response = requests.get(url)
            response.raise_for_status()
            liste_infractions = []
            csv_data = response.content.decode('utf-8')
            csv_reader = csv.DictReader(StringIO(csv_data))
            for row in csv_reader:
                date = datetime.strptime(row['date'], '%Y%m%d').date()
                date_jugement = datetime.strptime(
                    row['date_jugement'], '%Y%m%d').date()
                date_statut = datetime.strptime(
                    row['date_statut'], '%Y%m%d').date()
                infraction = Infractions(row['id_poursuite'],
                                         row['business_id'],
                                         date, row['description'],
                                         row['adresse'], date_jugement,
                                         row['etablissement'], row['montant'],
                                         row['proprietaire'], row['ville'],
                                         row['statut'], date_statut,
                                         row['categorie'])
                if get_db_infractions().creer_infraction(infraction):
                    liste_infractions.append(infraction)
                    destinataires = get_db_utilisateurs(
                    ).get_courriels_by_business_id(infraction.id_business)
                    if len(destinataires) > 0:
                        envoyer_courriel_etablissement(destinataires,
                                                       infraction)
            if len(liste_infractions) > 0:
                code = 201
                envoyer_courriel(liste_infractions)
                message = (f"La base de données a été mise à jour avec "
                           f"succès !\n"
                           f"{len(liste_infractions)} nouvelle(s) "
                           f"infraction(s) ont été rajoutée(s)")
            else:
                # Code 200, car aucune nouvelles rangées ont été insérées
                code = 200
                message = 'La base de données est déjà à jour'
            for infraction in liste_infractions:
                try:  # Gérer le cas d'un tweet qui rate
                    publier_tweet(infraction)
                except tweepy.TweepyException as e:
                    print(str(e))
            return message, code
        except Exception as e:
            return f'{MESSAGE_ERREUR_500} : {str(e)}', 500


# Ce script permet de lancer le scheduler qui permet de mettre a jour la
# base de donnees chaque jour a minuit A3
scheduler = BackgroundScheduler()
scheduler.add_job(index, 'cron', hour=00, minute=00, second=00)
scheduler.start()


# Cette route permet de rechercher les infractions dans la base de donnees
# selon le nom de l'etablissement, le proprietaire et la rue. Ensuite elle
# retourne les resultats dans un tableau dans une page web A2


@app.route('/api/recherche-infraction', methods=['POST'])
def recherche():
    try:
        nom_etablissement = request.form[
            'nomEtabnew FormData(formulaire)lissement']
        proprietaire = request.form['proprietaire']
        rue = request.form['rue']
        infractions = get_db_infractions().recherche_infraction(
            nom_etablissement,
            proprietaire, rue)
        if nom_etablissement == '' or proprietaire == '' or rue == '':
            return (
                'Veuillez entrer un nom d\'établissement, un propriétaire ou '
                'une rue'), 400
        if len(infractions) == 0:
            return 'Aucune infraction trouvée', 404
        return render_template('infraction.html', infractions=infractions), 200
    except Exception as e:
        return f'{MESSAGE_ERREUR_500} : {str(e)}', 500


# Cette route permet de recuperer les infractions selon une periode donnee
# et retourne les resultats en format json A4


@app.route('/api/contraventions')
def contraventions():
    date_debut = request.args.get('du')
    date_fin = request.args.get('au')
    infractions = get_db_infractions().get_infraction_by_date(date_debut,
                                                              date_fin)
    infractions_json = [infraction.__dict__ for infraction in infractions]
    return jsonify(infractions_json), 200


@app.route('/api/etablissement/<int:id_business>')
def etablissement(id_business):
    try:
        infractions = get_db_infractions().get_infraction_by_id_business(
            id_business)
        infractions_json = [infraction.__dict__ for infraction in infractions]
        if len(infractions_json) == 0:
            return 'Aucune infraction trouvée', 404
        else:
            return jsonify({"infractions": infractions_json,
                            "proprietaire": infractions[0].proprietaire,
                            "adresse": infractions[0].adresse,
                            "ville": infractions[0].ville}), 200
    except Exception as e:
        return f"MESSAGE_ERREUR_500 : {str(e)}", 500


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
    return render_template('doc.html'), 200


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
        "confirmation_mot_de_passe": "Les mots de passe ne correspondent pas "
                                     "ou ne sont pas valides",
    }
    dict_etablissements = get_db_infractions().get_all_etablissements()
    message = request.args.get('message', None)
    return render_template('inscription.html', nom_page='Inscription',
                           criteres_mdp=criteres_mdp,
                           liste=dict_etablissements, criteres=criteres,
                           message=message), 200


def authentifier_utilisateur(id_utilisateur: int):
    _id = uuid.uuid4().hex
    get_db_utilisateurs().creer_session(_id=_id, id_utilisateur=id_utilisateur)
    session['id'] = _id
    session['id_utilisateur'] = id_utilisateur


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
            hashed = hashlib.sha512(
                str(mot_de_passe + salt).encode("utf-8")).hexdigest()
            nouvel_utilisateur = Utilisateur(_id=None, prenom=prenom.strip(),
                                             nom=nom.strip(),
                                             courriel=courriel.strip(),
                                             salt=salt,
                                             _hash=hashed, photo=None,
                                             etablissements=_etablissements)
            id_utilisateur = get_db_utilisateurs().ajouter_utilisateur(
                nouvel_utilisateur)
            authentifier_utilisateur(id_utilisateur)
            message = "Inscription réussi !"
            code = 201
        else:
            message = f"L'adresse courriel \"{courriel}\" est déjà utilisée"
            code = 200
        return jsonify({"message": message, "code": code}), code

    except Exception as e:
        return jsonify(error=f"{MESSAGE_ERREUR_500} : {str(e)}"), 500


@app.route('/profil', methods=['GET'])
@authentification_requise
def profil():
    utilisateur_connecte = get_db_utilisateurs().get_utilisateur(
        session['id_utilisateur'])
    aide = {
        "prenom": "Vous ne pouvez pas modifier votre prénom",
        "nom": "Vous ne pouvez pas modifier votre nom",
        "courriel": "Vous ne pouvez pas modifier votre adresse courriel"
    }
    prenom = utilisateur_connecte.prenom
    nom = utilisateur_connecte.nom
    courriel = utilisateur_connecte.courriel
    _id = utilisateur_connecte.id
    id_etablissements_surveilles = utilisateur_connecte.etablissements
    _etablissements = []
    for id_etablissement in id_etablissements_surveilles:
        nom_etablissement = (get_db_infractions().
        get_etablissement_by_id_business(
            id_etablissement))
        _etablissements.append((id_etablissement, nom_etablissement))
    liste_tous_etablissements = get_db_infractions().get_all_etablissements()
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
    return render_template('profil.html', nom_page='Profil', id=_id,
                           prenom=prenom, nom=nom,
                           courriel=courriel, photo=photo_b64,
                           etablissements=_etablissements,
                           liste=liste_tous_etablissements, aide=aide), 200


def fichier_valide(fichier: werkzeug.datastructures.FileStorage) -> bool:
    return fichier.content_type in ['image/png', 'image/jpg', 'image/jpeg']


@app.route('/api/profil/modifer/<id>', methods=['PUT'])
@authentification_requise
def traitement_modifications(id):
    content_type = request.content_type.split(';')[0]
    if (content_type != 'multipart/form-data'
            and content_type != 'application/x-www-form-urlencoded'):
        return jsonify({'message': 'Le type de contenu est invalide'}), 400
    else:
        if get_db_utilisateurs().get_utilisateur(id):
            nouvelle_photo = False
            photo = request.files["photo"]
            _etablissements = request.form["liste_etablissements"]
            _etablissements = json.loads(_etablissements)
            if photo.filename != '':
                if fichier_valide(photo):
                    message = "Modifications apportées avec succès"
                    code = 200
                    nouvelle_photo = True
                    get_db_utilisateurs().modifier_utilisateur(id,
                                                               _etablissements,
                                                               photo)
                else:
                    message = (
                        f"Erreur lors de la lecture du fichier transmis : "
                        f"\"{photo.filename}\"")
                    code = 400
            else:
                message = "Modifications apportées avec succès"
                code = 200
                get_db_utilisateurs().modifier_utilisateur(id, _etablissements,
                                                           None)
            return jsonify(
                {"message": message, "code": code,
                 "photo": nouvelle_photo}), code
        else:
            abort(404)


@app.route('/login', methods=['GET', 'POST', 'PUT', 'PATCH'])
def login():
    return render_template('login.html',
                           message=request.args.get('message', None),
                           nom_page='Authentification'), 200


@app.route('/api/login/traitement', methods=['POST'])
@schema_utilisateur.validate(valider_login)
def traitement_login():
    try:
        data = request.get_json()
        courriel = data['courriel']
        mot_de_passe = data['mot_de_passe']
        id_utilisateur = get_db_utilisateurs().authentifier(courriel,
                                                            mot_de_passe)
        if id_utilisateur != -1:
            authentifier_utilisateur(id_utilisateur)
            return jsonify(), 200
        else:
            message = "Combinaison courriel et mot de passe invalide"
            return jsonify({'message': message}), 200
    except Exception as e:
        return jsonify(error=f"{MESSAGE_ERREUR_500} : {str(e)}"), 500


@app.route('/logout')
@authentification_requise
def logout():
    id_session = session['id']
    session.pop('id', None)
    session.pop('id_utilisateur', None)
    get_db_utilisateurs().supprimer_session(id_session)
    message_logout = "Vous avez été déconnecté avec succès"
    return redirect(url_for('home', message_logout=message_logout),
                    302)


@app.route('/api/demande-inspection', methods=['POST'])
@schema_inspection.validate(inspection_schema)
def demande_inspections():
    try:
        data = request.get_json()
        inspection = Inspection(None, data['etablissement'], data['adresse'],
                                data['ville'], data['date_visite_client'],
                                data['nom_client'], data['prenom_client'],
                                data['description_probleme'])
        inspection = get_db_infractions().inserer_plainte(inspection)
        return jsonify(inspection.asDictionary()), 201
    except Exception as e:
        return jsonify(error=F"{MESSAGE_ERREUR_500} : {str(e)}"), 500


@app.route('/api/supprimer-inspection/<int:id_inspection>', methods=['DELETE'])
def supprimer_inspection(id_inspection):
    try:
        get_db_infractions().supprimer_inspection(id_inspection)
        return jsonify(
            message='L\'inspection a été supprimée avec succès.'), 200
    except Exception as e:
        return jsonify(error=F"{MESSAGE_ERREUR_500} : {str(e)}"), 500


@app.route('/plainte')
def plainte():
    return render_template('plainte.html', nom_page='Plainte'), 200


@app.route('/api/retirer-etablissement/<string:etablissement>',
           methods=['DELETE'])
def retirer_etablissement(etablissement):
    etablissement = unquote(etablissement)
    try:
        if (request.authorization and request.authorization.username == 'admin'
                and request.authorization.password == 'admin'):
            get_db_infractions().supprimer_etablissement(etablissement)
            return jsonify(
                message='L\'établissement a été supprimé avec succès.'), 200
        else:
            return jsonify(error=MESSAGE_ERREUR_403), 403
    except Exception as e:
        return jsonify(error=F"{MESSAGE_ERREUR_500} : {str(e)}"), 500


@app.route('/modifier-etablissement/<string:etablissement>',
           methods=['GET', 'PUT'])
def modifier_etablissement(etablissement):
    etablissement = unquote(etablissement)
    try:
        if request.method == 'PUT':
            nouveau_nom = request.get_json()['nom_etablissement']
            get_db_infractions().modifier_etablissement(etablissement,
                                                        nouveau_nom)
            return jsonify(
                message='L\'établissement a été modifié avec succès.'), 200
        else:
            return render_template('modification_nom_etablissement.html',
                                   nom_page='Modifier établissement',
                                   etablissement=etablissement), 200
    except Exception as e:
        return jsonify(error=F"{MESSAGE_ERREUR_500} : {str(e)}"), 500


def envoyer_courriel_etablissement(destinataires: list,
                                   infraction: Infractions):
    objet = "Nouvelle infraction détectée"
    sender = app.config['MAIL_USERNAME']
    for destinataire in destinataires:
        nom_complet = get_db_utilisateurs().get_nom_by_courriel(destinataire)
        message = Message(subject=objet, sender=sender,
                          recipients=[destinataire])
        id_utilisateur = get_db_utilisateurs().get_id_by_courriel(destinataire)
        token = generer_token(id_utilisateur, infraction.id_business)
        message.html = render_template('courriels/courriel_etablissement.html',
                                       nom_complet=nom_complet,
                                       infraction=infraction,
                                       id_utilisateur=id_utilisateur,
                                       token=token,
                                       etablissement=infraction.id_business)
        mail.send(message)
        # Supprimer le token après 1 semaine
        moment_expiration = datetime.now() + timedelta(days=7)
        scheduler.add_job(supprimer_token, 'date', run_date=moment_expiration,
                          args=[token])


@app.route('/confirmer-suppression/<id_utilisateur>&<token>&<etablissement>')
def confirmer_suppression(id_utilisateur, token, etablissement):
    if get_db_utilisateurs().verifier_token(id_utilisateur, token,
                                            etablissement):
        donnees = get_db_infractions().get_adresse_ville_etablissement(
            etablissement)
        nom_etablissement = donnees[0]
        adresse = donnees[1]
        ville = donnees[2]
        # Supprimer le token 5 minute après l'accès à cette route
        moment_expiration = datetime.now() + timedelta(minutes=5)
        scheduler.add_job(supprimer_token, 'date', run_date=moment_expiration,
                          args=[token])
        return render_template('confirmation_suppression.html',
                               id_utilisateur=id_utilisateur, token=token,
                               etablissement=etablissement,
                               nom_etablissement=nom_etablissement,
                               adresse=adresse, ville=ville,
                               nom_page='Confirmer suppression'), 200
    else:
        abort(403)


def generer_token(id_utilisateur: int, etablissement: int) -> str or None:
    if get_db_utilisateurs().get_utilisateur(id_utilisateur) is not None:
        return get_db_utilisateurs().generer_token(id_utilisateur,
                                                   etablissement)
    else:
        return None


def supprimer_token(token: str):
    # Envelopper le code dans un contexte d'application Flask
    with app.app_context():
        get_db_utilisateurs().supprimer_token(token)


@app.route(
    '/api/supprimer-etablissement/<id_utilisateur>&<token>&<etablissement>',
    methods=["PATCH"])
def supprimer_etablissement(id_utilisateur: int, token: str,
                            etablissement: int):
    if get_db_utilisateurs().verifier_token(id_utilisateur, token,
                                            etablissement):
        etablissements_surveilles = (get_db_utilisateurs().
        get_all_etablissements_surveilles(
            id_utilisateur))
        if int(etablissement) in etablissements_surveilles:
            etablissements_surveilles.remove(int(etablissement))
        get_db_utilisateurs().modifier_utilisateur(id_utilisateur,
                                                   etablissements_surveilles,
                                                   None)
        message = "L'établissement a été supprimé de votre profil"
        code = 200
        supprimer_token(token)
    else:
        message = "Le jeton d'authentification fourni est invalide ou a expiré"
        code = 403
    return jsonify({"message": message, "code": code}), code


@app.route('/api/infractions-etablissements/<format>', methods=['GET'])
def infractions_etablissements(format):
    etablissements = get_db_infractions().get_infractions_etablissement()
    if etablissements:
        if format == "json":
            reponse_json = []
            for _etablissement in etablissements:
                reponse_json.append({
                    "nom": _etablissement[2],
                    "id": _etablissement[0],
                    "nombre_infractions": _etablissement[1]
                })
            return jsonify(reponse_json), 200
        elif format == "xml":
            racine = ET.Element("etablissements")
            # Ajouter les éléments à l'arbre XML
            for _etablissement in etablissements:
                etablissement_xml = ET.SubElement(racine, 'etablissement')
                ET.SubElement(etablissement_xml, 'nom').text = _etablissement[
                    2]
                ET.SubElement(etablissement_xml, 'id').text = str(
                    _etablissement[0])
                ET.SubElement(etablissement_xml,
                              'nombre_infractions').text = str(
                    _etablissement[1])
            # Générer la réponse XML
            xml_string = ET.tostring(racine, encoding='utf-8', method='xml')
            # Créer une réponse avec le contenu XML et le type de contenu
            # approprié
            response = make_response(xml_string)
            response.headers['Content-Type'] = 'application/xml'
            return response, 200
        elif format == "csv":
            # Insérer le tuple qui représente les titres des colonnes
            etablissements.insert(0, ("ID", "Nombre d'infractions", "Nom"))

            # Créer le contenu CSV
            donnees_csv = io.StringIO()
            csv_writer = csv.writer(donnees_csv)
            csv_writer.writerows(etablissements)

            # Créer la réponse avec le contenu CSV
            response = make_response(donnees_csv.getvalue())

            # Spécifier l'encodage UTF-8 dans les en-têtes de la réponse
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers[
                'Content-Disposition'] = 'attachment; filename=infractions.csv'
            return response, 200
        else:
            jsonify({"message": f"Le format \"{format}\" "
                                f"n'est pas supporté par ce service"}), 400


@app.errorhandler(404)
def page_not_found(error):
    return render_template('erreur.html', message_erreur=MESSAGE_ERREUR_404,
                           titre="Erreur 404", nom_page=f"{str(error)}"), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('erreur.html', message_erreur=MESSAGE_ERREUR_405,
                           titre="Erreur 405", nom_page=f"{str(error)}"), 405


@app.errorhandler(403)
def access_denied(error):
    return render_template('erreur.html', message_erreur=MESSAGE_ERREUR_403,
                           titre="Erreur 403", nom_page=f"{str(error)}"), 403


@app.errorhandler(500)
def servor_error(error):
    return render_template('erreur.html', message_erreur=f"{MESSAGE_ERREUR_500} : {str(error)}",
                           titre="Erreur 500", nom_page=f"{str(error)}"), 500