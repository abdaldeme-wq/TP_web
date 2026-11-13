from pydantic import BaseModel


class Pokemon(BaseModel):
    """Fiche d'un Pokémon telle que renvoyée par l'API."""

    number: int
    name: str
    name_fr: str
    types: list[str]
    image_url: str
    height: int
    weight: int
    evolves_from_number: int | None = None


class PokemonType(BaseModel):
    """Type de Pokémon mis en cache dans SQLite (ex : electric -> Électrik)."""

    id: int
    name: str
    name_fr: str
