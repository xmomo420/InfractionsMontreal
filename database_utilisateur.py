import hashlib
import secrets
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

    def creer_session(self, _id, id_utilisateur) -> None:
        connection = self.get_connection()
        connection.execute("INSERT INTO Sessions "
                           "(id, id_utilisateur) VALUES (?, ?)",
                           (_id, id_utilisateur))
        connection.commit()

    def supprimer_session(self, _id) -> None:
        connection = self.get_connection()
        connection.execute("DELETE FROM Sessions WHERE id == ?",
                           (_id,))
        connection.commit()

    def get_session(self, _id) -> str:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM Sessions WHERE id == ?",
                       (_id,))
        donnee = cursor.fetchone()
        return donnee[0]

    def get_utilisateur(self, _id) -> Utilisateur or None:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM Utilisateurs WHERE id == ?", (_id,))
        donnee = cursor.fetchone()
        if donnee:
            liste_etablissements = json.loads(donnee[7])
            return Utilisateur(_id=donnee[0], prenom=donnee[1], nom=donnee[2], courriel=donnee[3], photo=donnee[6],
                               etablissements=liste_etablissements, salt=None, _hash=None)
        else:
            return None

    def authentifier(self, courriel: str, mot_de_passe: str) -> int:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM Utilisateurs WHERE courriel == ?", (courriel,))
        utilisateur = cursor.fetchone()
        if utilisateur:
            salt = utilisateur[5]
            _hash = utilisateur[4]
            if _hash == hashlib.sha512(
                    str(mot_de_passe + salt).encode("utf-8")).hexdigest():
                _id = utilisateur[0]
            else:
                _id = -1
        else:
            _id = -1
        return _id

    def modifier_utilisateur(self, _id, etablissements, photo) -> bool:
        connection = self.get_connection()
        etablissements_json = json.dumps(etablissements)
        if photo is not None:
            photo_blob = sqlite3.Binary(photo.read())
            connection.execute("UPDATE Utilisateurs SET etablissements = ?, photo = ? WHERE id == ?",
                               (etablissements_json, photo_blob, _id))
        else:
            connection.execute("UPDATE Utilisateurs SET etablissements = ? WHERE id == ?",
                               (etablissements_json, _id))
        connection.commit()
        cursor = connection.cursor()
        return cursor.rowcount > 0

    def get_nom_by_courriel(self, courriel: str) -> str:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT prenom, nom FROM Utilisateurs WHERE courriel = ?", (courriel,))
        donnee = cursor.fetchone()
        return donnee[0] + ' ' + donnee[1] if donnee else ''

    def get_courriels_by_business_id(self, id_business: int) -> list:
        cursor = self.get_connection().cursor()
        cursor.execute(
            "SELECT courriel FROM Utilisateurs, json_each(Utilisateurs.etablissements) "
            "AS etab WHERE etab.value = ?", (int(id_business),))
        donnees = cursor.fetchall()
        courriels = []
        for donnee in donnees:
            if donnee:
                courriels.append(donnee[0])
        return courriels

    def generer_token(self, id_utilisateur) -> str:
        token = secrets.token_urlsafe(16)
        connection = self.get_connection()
        connection.execute("INSERT INTO TokensSuppression (token, id_utilisateur) VALUES (?, ?)",
                           (token, id_utilisateur))
        connection.commit()
        cursor = connection.cursor()
        return token

    def supprimer_token(self, token: str, id_utilisateur: int):
        connection = self.get_connection()
        connection.execute("DELETE FROM TokensSuppression WHERE token = ? AND id_utilisateur = ?",
                           (token, id_utilisateur))
        connection.commit()

    def get_id_by_courriel(self, destinataire) -> int:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT id FROM Utilisateurs WHERE courriel == ?", (destinataire,))
        id_utilisateur = cursor.fetchone()
        if id_utilisateur:
            return id_utilisateur[0]
        else:
            return -1

    def verifier_token(self, id_utilisateur, token) -> bool:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM TokensSuppression "
                       "WHERE id_utilisateur == ? AND token == ?", (id_utilisateur, token))
        donnee = cursor.fetchone()
        return True if donnee is not None else False

    def get_all_etablissements_surveilles(self, id_utilisateur) -> list:
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT etablissements FROM Utilisateurs WHERE id == ?", (id_utilisateur,))
        donnnes = cursor.fetchone()
        return json.loads(donnnes[0])
