from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.security import verify_token
from repositories.pokemon_repository import get_all_pokemons, get_pokemon_by_number
from schemas.pokemon import Pokemon
from services.pokemon_service import (
    PokeApiError,
    PokeApiUnavailableError,
    PokemonAlreadyExistsError,
    PokemonNotFoundError,
    scan_pokemon,
)

app = FastAPI()

# Partie 16 : autoriser les pages HTML (autre origine) à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def to_http_error(error: Exception) -> HTTPException:
    """Traduit une erreur métier du service en réponse HTTP."""
    if isinstance(error, PokemonAlreadyExistsError):
        return HTTPException(status_code=404, detail="Pokémon déjà enregistré")
    if isinstance(error, PokemonNotFoundError):
        return HTTPException(status_code=404, detail="Pokémon introuvable")
    if isinstance(error, PokeApiUnavailableError):
        return HTTPException(status_code=503, detail="PokéAPI est indisponible")
    return HTTPException(status_code=502, detail="Erreur renvoyée par PokéAPI")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/pokemons", response_model=list[Pokemon])
def list_pokemons():
    # Partie 14 : uniquement les Pokémon enregistrés dans SQLite, jamais PokéAPI
    return get_all_pokemons()


@app.get("/pokemons/{number}", response_model=Pokemon)
def get_pokemon(number: int):
    # Partie 13 : lecture dans SQLite uniquement, aucun appel à PokéAPI
    pokemon = get_pokemon_by_number(number)
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon non enregistré")
    return pokemon


# Partie 15 : le scan est protégé par le jeton Bearer
@app.get(
    "/pokemons/{number}/scan",
    response_model=Pokemon,
    dependencies=[Depends(verify_token)],
)
def scan(number: int):
    try:
        return scan_pokemon(number)
    except (PokemonAlreadyExistsError, PokemonNotFoundError,
            PokeApiError, PokeApiUnavailableError) as error:
        raise to_http_error(error)
