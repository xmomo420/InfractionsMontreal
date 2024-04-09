class Utilisateur:

    def __init__(self,
                 _id,
                 prenom: str,
                 nom: str,
                 courriel: str,
                 _hash,
                 salt,
                 photo,
                 etablissements):
        self.id = _id
        self.prenom = prenom
        self.nom = nom
        self.courriel = courriel
        self.hashed = _hash
        self.salt = salt
        self.photo = photo
        self.etablissements = etablissements
