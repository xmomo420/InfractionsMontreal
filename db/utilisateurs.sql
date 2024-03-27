CREATE TABLE Utilisateurs (
    id INTEGER PRIMARY KEY,
    prenom TEXT NOT NULL,
    nom TEXT NOT NULL,
    courriel TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    photo BLOB,
    etablissements TEXT NOT NULL
)