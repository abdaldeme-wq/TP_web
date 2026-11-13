from db.database import get_connection


def get_type_by_name(name: str) -> dict | None:
    """Renvoie le type mis en cache (ex : "electric"), ou None s'il est absent."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM pokemon_types WHERE name = ?", (name,)
        ).fetchone()
    return dict(row) if row else None


def insert_type(pokemon_type: dict) -> None:
    """Enregistre un type et sa traduction française dans le cache."""
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO pokemon_types (id, name, name_fr) VALUES (:id, :name, :name_fr)",
            pokemon_type,
        )
