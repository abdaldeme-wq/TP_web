# Pokédex — API REST (FastAPI)

Backend d'un Pokédex de la **première génération** (151 Pokémon), réalisé dans le cadre du TP
« Développer un Pokédex avec une API REST » (ENSEA, FISA 3A).

Technologies : **Python, FastAPI, Pydantic, SQLite, requests** et **[PokéAPI](https://pokeapi.co/)**.

Le Pokédex est vide au départ : un Pokémon n'est récupéré sur PokéAPI qu'au moment où un
utilisateur demande son **scan**, puis il est enregistré dans SQLite.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python create_database.py
```

## Lancement

```bash
fastapi dev main.py
```

Documentation interactive : http://127.0.0.1:8000/docs

## Routes

| Méthode | Route | Description | Protégée |
|---|---|---|---|
| GET | `/health` | État de l'API : `{"status": "ok"}` | Non |
| GET | `/pokemons` | Liste des Pokémon enregistrés dans SQLite | Non |
| GET | `/pokemons/{number}` | Fiche d'un Pokémon enregistré (404 s'il est absent) | Non |
| GET | `/pokemons/{number}/scan` | Récupère un Pokémon sur PokéAPI et l'enregistre | **Oui** |

La route de scan exige l'en-tête :

```
Authorization: Bearer ENSEA2026
```

Codes d'erreur : `401` jeton absent ou invalide, `404` Pokémon inexistant, non enregistré ou
déjà enregistré, `502` erreur de PokéAPI, `503` PokéAPI indisponible.

## Architecture

```
pokedex/
├── main.py                          # Application FastAPI et routes HTTP
├── create_database.py               # Création des tables SQLite
├── schemas/
│   └── pokemon.py                   # Modèles Pydantic (Pokemon, PokemonType)
├── services/
│   └── pokemon_service.py           # Logique métier du scan et normalisation
├── repositories/
│   ├── pokemon_repository.py        # Requêtes SQL sur la table pokemon
│   └── pokemon_type_repository.py   # Requêtes SQL sur le cache pokemon_types
├── clients/
│   └── pokeapi.py                   # Communication avec PokéAPI
├── db/
│   └── database.py                  # Connexion SQLite
└── core/
    └── security.py                  # Vérification du jeton Bearer
```

Trajet d'un scan : route FastAPI → service métier → client PokéAPI et repository → PokéAPI et SQLite.

## Données enregistrées

Chaque fiche contient : numéro, nom PokéAPI, **nom français**, **types traduits en français**,
image, taille (cm), poids (g) et numéro de l'évolution précédente. Les pré-évolutions ajoutées
après la Gen 1 (ex : Pichu #172 pour Pikachu) sont ignorées.

Les traductions de types sont mises en **cache dans SQLite** (table `pokemon_types`) : chaque type
n'est demandé qu'une seule fois à PokéAPI, même après un redémarrage du serveur.
