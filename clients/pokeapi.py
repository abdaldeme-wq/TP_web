import requests

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
TIMEOUT = 10  # secondes


def _get_json(path: str) -> dict:
    """Effectue un GET sur PokéAPI et renvoie le JSON.

    Lève requests.HTTPError si PokéAPI répond avec une erreur (ex : 404),
    ou requests.RequestException si PokéAPI est injoignable.
    """
    # 1. Construire l'URL
    url = f"{POKEAPI_BASE_URL}/{path}"

    # 2. Effectuer la requête HTTP
    response = requests.get(url, timeout=TIMEOUT)

    # 3. Détecter les erreurs HTTP (404, 500...)
    response.raise_for_status()

    # 4. Renvoyer les données JSON
    return response.json()


def get_pokemon_from_api(number: int) -> dict:
    """Informations principales : id, name, types, sprites, height, weight."""
    return _get_json(f"pokemon/{number}")


def get_pokemon_species_from_api(number: int) -> dict:
    """Espèce du Pokémon : noms traduits (names) et evolves_from_species."""
    return _get_json(f"pokemon-species/{number}")


def get_type_from_api(type_name: str) -> dict:
    """Type (ex : electric) : contient ses noms traduits (names)."""
    return _get_json(f"type/{type_name}")
