import json
import sqlite3

from db.database import get_connection


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convertit une ligne SQLite en dictionnaire Python."""
    pokemon = dict(row)
    # Les types sont stockés en texte JSON : on les reconvertit en liste
    pokemon["types"] = json.loads(pokemon["types"])
    return pokemon


def get_pokemon_by_number(number: int) -> dict | None:
    """Renvoie le Pokémon enregistré sous ce numéro, ou None s'il est absent."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM pokemon WHERE number = ?", (number,)
        ).fetchone()
    return _row_to_dict(row) if row else None


def get_all_pokemons() -> list[dict]:
    """Renvoie tous les Pokémon enregistrés, triés par numéro."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM pokemon ORDER BY number"
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def insert_pokemon(pokemon: dict) -> None:
    """Enregistre une fiche Pokémon dans la base."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO pokemon
                (number, name, name_fr, types, image_url, height, weight, evolves_from_number)
            VALUES
                (:number, :name, :name_fr, :types, :image_url, :height, :weight, :evolves_from_number)
            """,
            {**pokemon, "types": json.dumps(pokemon["types"], ensure_ascii=False)},
        )