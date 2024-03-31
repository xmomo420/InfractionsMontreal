CREATE TABLE Utilisateurs (
    id INTEGER PRIMARY KEY,
    prenom TEXT NOT NULL,
    nom TEXT NOT NULL,
    courriel TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    photo BLOB,
    etablissements TEXT NOT NULL
);

CREATE TABLE Sessions (
    id VARCHAR(32) PRIMARY KEY,
    id_utilisateur INTEGER NOT NULL,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateurs(id)
);

CREATE TABLE TokensSuppression (
    token VARCHAR(32) PRIMARY KEY,
    id_utilisateur INTEGER NOT NULL,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateurs(id)
);

