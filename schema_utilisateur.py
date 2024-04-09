valider_nouvel_utilisateur = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "prenom": {
            "type": "string",
            "minLength": 1
        },
        "nom": {
            "type": "string",
            "minLength": 1
        },
        "courriel": {
            "type": "string",
            "format": "email"
        },
        "confirmation_courriel": {
            "type": "string",
            "pattern": r"^\S+@\S+\.\S+$"
        },
        "mot_de_passe": {
            "type": "string",
            "minLength": 8,
            "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*"
            "[!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>\\/?]).{8,}$"
        },
        "etablissements": {
            "type": "array",
            "items": {"type": "number"}
        }
    },
    "required": ["prenom",
                 "nom",
                 "courriel",
                 "mot_de_passe",
                 "etablissements"],
    "additionalProperties": False,
}

valider_login = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "courriel": {
            "type": "string",
            "pattern": r"^\S+@\S+\.\S+$"
        },
        "mot_de_passe": {
            "type": "string",
            "minLength": 1
        }
    },
    "required": ["courriel", "mot_de_passe"],
    "additionalProperties": False,
}
