import requests

from clients.pokeapi import (
    get_pokemon_from_api,
    get_pokemon_species_from_api,
    get_type_from_api,
)
from repositories.pokemon_repository import get_pokemon_by_number, insert_pokemon
from repositories.pokemon_type_repository import get_type_by_name, insert_type
from schemas.pokemon import Pokemon, PokemonType

GEN1_MAX_NUMBER = 151


# --- Erreurs métier : le service ne connaît pas HTTP, main.py les traduit ---

class PokemonAlreadyExistsError(Exception):
    """Le Pokémon est déjà enregistré dans le Pokédex."""


class PokemonNotFoundError(Exception):
    """Le Pokémon n'existe pas chez PokéAPI."""


class PokeApiError(Exception):
    """PokéAPI a renvoyé une erreur."""


class PokeApiUnavailableError(Exception):
    """PokéAPI est injoignable."""


# --- Normalisation des données (partie 11) ---

def get_french_name(names: list[dict], default: str) -> str:
    """Cherche l'entrée dont language.name == "fr" ; sinon renvoie le nom par défaut."""
    for entry in names:
        if entry["language"]["name"] == "fr":
            return entry["name"]
    return default


def get_evolves_from_number(species: dict) -> int | None:
    """Numéro du Pokémon dont il évolue, limité à la Gen 1 (1 à 151)."""
    parent = species["evolves_from_species"]
    if parent is None:
        return None  # pas d'évolution précédente (ex : Bulbizarre)

    # L'URL se termine par le numéro : ".../pokemon-species/172/" -> 172
    number = int(parent["url"].rstrip("/").split("/")[-1])

    # Pré-évolution ajoutée après la Gen 1 (ex : Pichu #172) -> ignorée
    if number > GEN1_MAX_NUMBER:
        return None
    return number


def translate_type(type_name: str) -> str:
    """Traduit un type en français en passant par le cache SQLite (partie 12.5)."""
    # 1. Type déjà en cache : on réutilise sa traduction, sans appeler PokéAPI
    cached_type = get_type_by_name(type_name)
    if cached_type is not None:
        return cached_type["name_fr"]

    # 2. Type absent : on interroge PokéAPI puis on l'enregistre pour la suite
    type_data = get_type_from_api(type_name)
    pokemon_type = PokemonType(
        id=type_data["id"],
        name=type_data["name"],
        name_fr=get_french_name(type_data["names"], type_name),
    )
    insert_type(pokemon_type.model_dump())
    return pokemon_type.name_fr


def fetch_pokemon(number: int) -> Pokemon:
    """Récupère un Pokémon sur PokéAPI et le convertit au format de l'application."""
    try:
        data = get_pokemon_from_api(number)
        species = get_pokemon_species_from_api(number)
        types_fr = [translate_type(t["type"]["name"]) for t in data["types"]]
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            raise PokemonNotFoundError(number)
        raise PokeApiError(number)
    except requests.RequestException:
        raise PokeApiUnavailableError(number)

    return Pokemon(
        number=data["id"],
        name=data["name"],
        name_fr=get_french_name(species["names"], data["name"]),
        types=types_fr,
        image_url=data["sprites"]["front_default"] or "",
        height=data["height"] * 10,    # décimètres -> centimètres
        weight=data["weight"] * 100,   # hectogrammes -> grammes
        evolves_from_number=get_evolves_from_number(species),
    )


# --- Règles métier du scan (partie 12) ---

def scan_pokemon(number: int) -> Pokemon:
    """Scanne UN Pokémon : vérifie l'absence de doublon, le récupère et l'enregistre."""
    # 1. Déjà enregistré -> pas de doublon
    if get_pokemon_by_number(number) is not None:
        raise PokemonAlreadyExistsError(number)

    # 2-3. Absent -> récupérer les données externes et les normaliser
    pokemon = fetch_pokemon(number)

    # 4. Enregistrer la fiche
    insert_pokemon(pokemon.model_dump())

    # 5. Renvoyer les données enregistrées
    return pokemon
