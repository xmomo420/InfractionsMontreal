inspection_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "etablissement": {"type": "string"},
        'adresse': {'type': 'string'},
        'ville': {'type': 'string'},
        'date_visite_client': {'type': 'string'},
        'nom_client': {'type': 'string'},
        'prenom_client': {'type': 'string'},
        'description_probleme': {'type': 'string'},
    },
    'required': ['etablissement',
                 'adresse',
                 'ville',
                 'date_visite_client',
                 'nom_client',
                 'prenom_client',
                 'description_probleme'],
    'additionalProperties': False
}
