import sqlite3
from infractions import Infractions


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/infractions.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def creer_infraction(self, infraction):
        cursor = self.get_connection().cursor()
        cursor.execute("INSERT INTO infractions (id_poursuite, id_business, date, description, adresse, date_jugement, etablissement, montant, proprietaire, ville, statut, date_statut, categorie) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (infraction.id_poursuite, infraction.id_business, infraction.date, infraction.description, infraction.adresse, infraction.date_jugement, infraction.etablissement, infraction.montant, infraction.proprietaire, infraction.ville, infraction.statut, infraction.date_statut, infraction.categorie))
        self.get_connection().commit()

    def recherche_infraction(self, nomEtablissement, proprietaire, rue):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM infractions WHERE etablissement LIKE ? AND proprietaire LIKE ? AND adresse LIKE ?", ('%'+nomEtablissement+'%', '%'+proprietaire+'%', '%'+rue+'%',))
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction) for infraction in infractions_data]
        return infractions

    def get_infraction_by_date(self, date_debut, date_fin):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM infractions WHERE date BETWEEN ? AND ?", (date_debut, date_fin,))
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction) for infraction in infractions_data]
        return infractions