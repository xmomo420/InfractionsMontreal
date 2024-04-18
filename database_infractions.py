import sqlite3
from infractions import Infractions
from demande_inspection import Inspection


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

    # Retourne true si l'infraction n'existait pas
    def creer_infraction(self, infraction) -> bool:
        cursor = self.get_connection().cursor()
        cursor.execute(
            "INSERT INTO infractions (id_poursuite, id_business, date, "
            " description, adresse, date_jugement, "
            "etablissement, montant, proprietaire, ville, statut,"
            " date_statut, categorie)"
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT (id_poursuite) DO NOTHING",
            (infraction.id_poursuite,
             infraction.id_business,
             infraction.date,
             infraction.description,
             infraction.adresse,
             infraction.date_jugement,
             infraction.etablissement,
             infraction.montant,
             infraction.proprietaire,
             infraction.ville,
             infraction.statut,
             infraction.date_statut,
             infraction.categorie))
        self.get_connection().commit()
        # L'infraction existait déjà
        return cursor.lastrowid == int(infraction.id_poursuite)

    def get_infractions(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM infractions")
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction)
                       for infraction in infractions_data]
        return infractions

    def recherche_infraction(self, nomEtablissement, proprietaire, rue):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT * FROM infractions WHERE etablissement "
            "LIKE ? AND proprietaire LIKE ? AND adresse LIKE ?",
            ('%' + nomEtablissement + '%', '%' + proprietaire + '%',
             '%' + rue + '%',))
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction)
                       for infraction in infractions_data]
        return infractions

    def get_infraction_by_date(self, date_debut, date_fin):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT * FROM infractions WHERE date BETWEEN ? AND ?",
            (date_debut, date_fin,))
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction)
                       for infraction in infractions_data]
        return infractions

    def get_infraction_by_id_business(self, id_business):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT * FROM infractions WHERE id_business = ?",
            (id_business,))
        infractions_data = cursor.fetchall()
        infractions = [Infractions(*infraction)
                       for infraction in infractions_data]
        return infractions

    def get_all_etablissements(self) -> list:
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT DISTINCT id_business, etablissement FROM infractions "
            "ORDER BY etablissement COLLATE NOCASE")
        donnees = cursor.fetchall()
        return donnees

    def get_etablissement_by_id_business(self, id_business) -> str:
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT etablissement FROM Infractions "
            "WHERE id_business == ?", (id_business,))
        donnees = cursor.fetchone()
        return donnees[0]

    def inserer_plainte(self, plainte):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "INSERT INTO Demande_inspection (etablissement, adresse,"
            " ville, date_visite, nom_client, prenom_client, description)"
            " VALUES (?,?,?,?,?,?,?)",
            (plainte.etablissement,
             plainte.adresse,
             plainte.ville,
             plainte.date_visite_client,
             plainte.nom_client,
             plainte.prenom_client,
             plainte.description_probleme))
        self.get_connection().commit()
        cursor = cursor.execute("SELECT last_insert_rowid()")
        result = cursor.fetchall()
        plainte.id = result[0][0]
        return plainte

    def supprimer_inspection(self, id_inspection):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "DELETE FROM Demande_inspection WHERE id = ?", (id_inspection,))
        self.get_connection().commit()

    def supprimer_etablissement(self, etablissement):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "DELETE FROM infractions WHERE etablissement = ?",
            (etablissement,))
        self.get_connection().commit()

    def get_adresse_ville_etablissement(self, id_business) -> tuple:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT etablissement, adresse, ville "
                       "FROM infractions WHERE id_business = ? LIMIT 1",
                       (id_business,))
        donnees = cursor.fetchone()
        return donnees

    def get_infractions_etablissement(self) -> list or None:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT id_business, COUNT(*) AS occurences, "
                       "etablissement FROM Infractions "
                       "GROUP BY id_business, etablissement"
                       " ORDER BY occurences DESC")
        donnees = cursor.fetchall()
        return donnees if len(donnees) > 0 else None

    def modifier_etablissement(self, etablissement, nouveau_nom):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "UPDATE infractions SET etablissement = ? "
            "WHERE etablissement = ?",
            (nouveau_nom, etablissement))
        self.get_connection().commit()

    def infractions_empty(self) -> bool:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM infractions")
        infractions_data = cursor.fetchall()
        return len(infractions_data) == 0
