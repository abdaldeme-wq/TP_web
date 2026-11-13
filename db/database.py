import sqlite3
from pathlib import Path

# Chemin absolu vers pokedex.db (dossier parent de db/)
DATABASE_PATH = Path(__file__).resolve().parent.parent / "pokedex.db"


def get_connection() -> sqlite3.Connection:
    """Ouvre une connexion à la base SQLite du Pokédex."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection