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

    def creer_session(self, _id, id_utilisateur):
        connection = self.get_connection()
        connection.execute("INSERT INTO Sessions "
                           "(id, id_utilisateur) VALUES (?, ?)",
                           (_id, id_utilisateur))
        connection.commit()

    def supprimer_session(self, _id):
        connection = self.get_connection()
        connection.execute("DELETE FROM Sessions WHERE id = ?",
                           (_id,))
        connection.commit()

    def get_session(self, _id):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM Sessions WHERE id = ?",
                       (_id,))
        donnee = cursor.fetchone()
        return donnee[0]

    def get_utilisateur(self, _id) -> Utilisateur:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM Utilisateurs WHERE id == ?", (_id,))
        donnee = cursor.fetchone()
        liste_etablissements = json.loads(donnee[7])
        return Utilisateur(_id=donnee[0], prenom=donnee[1], nom=donnee[2], courriel=donnee[3], photo=donnee[6],
                           etablissements=liste_etablissements, salt=None, _hash=None)



