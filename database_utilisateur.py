import sqlite3
import json

from utilisateur import Utilisateur


class DatabaseUtilisateur:

    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/utilisateurs.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def ajouter_utilisateur(self, utilisateur: Utilisateur) -> int:
        etablissements_json = json.dumps(utilisateur.etablissements)
        cursor = self.get_connection().cursor()
        cursor.execute("INSERT INTO Utilisateurs (prenom, nom, courriel, hash, salt, etablissements) "
                       " VALUES (?,?,?,?,?,?)", (utilisateur.prenom, utilisateur.nom, utilisateur.courriel,
                                                 utilisateur.hashed, utilisateur.salt, etablissements_json))
        id_genere = cursor.lastrowid
        self.get_connection().commit()
        return id_genere

    def get_all_courriels(self) -> list:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT courriel FROM Utilisateurs")
        courriels = cursor.fetchall()
        liste_courriels = []
        for courriel in courriels:
            liste_courriels.append(courriel[0])
        return liste_courriels
