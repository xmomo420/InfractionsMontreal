from flask import Flask, g
import requests
from database import Database
from infractions import Infractions
from datetime import datetime
from io import StringIO
import csv

app = Flask(__name__)


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


# Cette route permet de recuperer les donnees du fichier csv et les insere dans la base de donnees  A1
@app.route('/api/infractions-csv-to-db')
def index():
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
    return 'La base de données a été mise à jour avec succès!', 201



