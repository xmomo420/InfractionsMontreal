valider_nouvel_utilisateur = {
    "type": "object",
    "properties": {
        "prenom": {"type": "string"},
        "nom": {"type": "string"},
        "courriel": {
            "type": "string",
            "format": "email"
        },
        "confirmation_courriel": {
            "type": "string",
            "format": "email"
        },
        "mot_de_passe": {
            "type": "string",
            "minLength": 8,
            "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>\\/?]).{8,}$"
        },
        "confirmation_mot_de_passe": {
            "type": "string",
            "minLength": 8,
            "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>\\/?]).{8,}$"
        },
        "etablissements": {
            "type": "array",
            "items": {"type": "string"}
        },
        "photo": {
            "type": "string",
            "contentEncoding": "base64",
            "contentMediaType": "image/jpeg|image/png|image/jpg"
        }
    },
    "required": ["prenom", "nom", "courriel", "mot_de_passe", "etablissements"],
    "additionalProperties": False,
    "dependencies": {
        "confirmation_courriel": {
            "properties": {
                "courriel": {"const": {"$data": "confirmation_courriel"}}
            }
        },
        "confirmation_mot_de_passe": {
            "properties": {
                "mot_de_passe": {"const": {"$data": "confirmation_mot_de_passe"}}
            }
        }
    }
}
