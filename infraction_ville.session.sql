CREATE TABLE Infractions (
    id INTEGER PRIMARY KEY,
    id_poursuite integer,
    id_business integer,
    date timestamp,
    description text,
    adresse text,
    date_jugement timestamp,
    etablissement text,
    montant  int,
    proprietaire text,
    ville text,
    statut text,
    date_statut timestamp,
    categorie text
)