import sqlite3
from infractions import Infractions


class DatabaseInfractions:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/infractions.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def creer_infraction(self, infraction) -> bool:  # Retourne true si l'infraction n'existait pas
        cursor = self.get_connection().cursor()
        cursor.execute(
            "INSERT INTO infractions (id_poursuite, id_business, date, description, adresse, date_jugement, "
            "etablissement, montant, proprietaire, ville, statut, date_statut, categorie)"
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT (id_poursuite) DO NOTHING",
            (infraction.id_poursuite, infraction.id_business, infraction.date, infraction.description,
             infraction.adresse, infraction.date_jugement, infraction.etablissement, infraction.montant,
             infraction.proprietaire, infraction.ville, infraction.statut, infraction.date_statut,
             infraction.categorie))
        self.get_connection().commit()
        return cursor.lastrowid == int(infraction.id_poursuite)  # L'infraction existait déjà

    def get_infractions(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM infractions")
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction) for infraction in infractions_data]
        return infractions

    def recherche_infraction(self, nomEtablissement, proprietaire, rue):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT * FROM infractions WHERE etablissement LIKE ? AND proprietaire LIKE ? AND adresse LIKE ?",
            ('%' + nomEtablissement + '%', '%' + proprietaire + '%', '%' + rue + '%',))
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction) for infraction in infractions_data]
        return infractions

    def get_infraction_by_date(self, date_debut, date_fin):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM infractions WHERE date BETWEEN ? AND ?", (date_debut, date_fin,))
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction) for infraction in infractions_data]
        return infractions

    def get_infraction_by_id_business(self, id_business):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM infractions WHERE id_business = ?", (id_business,))
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction) for infraction in infractions_data]
        return infractions

    def get_all_etablissements(self) -> list:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT DISTINCT id_business, etablissement FROM infractions")
        donnees = cursor.fetchall()
        return donnees

    def get_etablissement_by_id_business(self, id_business) -> str:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT etablissement FROM Infractions WHERE id_business == ?", (id_business,))
        donnees = cursor.fetchone()
        return donnees[0]

    def get_adresse_ville_etablissement(self, id_business) -> tuple:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT etablissement, adresse, ville FROM infractions WHERE id_business = ? LIMIT 1",
                       (id_business,))
        donnees = cursor.fetchone()
        return donnees
