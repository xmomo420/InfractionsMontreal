class Inspection:
    def __init__(self,
                 id,
                 etablissement,
                 adresse,
                 ville,
                 date_visite_client,
                 nom_client,
                 prenom_client,
                 description_probleme):
        self.id = id
        self.etablissement = etablissement
        self.adresse = adresse
        self.ville = ville
        self.date_visite_client = date_visite_client
        self.nom_client = nom_client
        self.prenom_client = prenom_client
        self.description_probleme = description_probleme

    def asDictionary(self):
        return {
            'id': self.id,
            'etablissement': self.etablissement,
            'adresse': self.adresse,
            'ville': self.ville,
            'date_visite_client': self.date_visite_client,
            'nom_client': self.nom_client,
            'prenom_client': self.prenom_client,
            'description_probleme': self.description_probleme
        }
