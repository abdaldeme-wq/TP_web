import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Jeton fixe : suffisant pour le TP, pas pour une application publique
API_TOKEN = "ENSEA2026"

# Lit l'en-tête "Authorization: Bearer <jeton>".
# auto_error=False : c'est nous qui renvoyons l'erreur 401 si le jeton manque.
bearer_scheme = HTTPBearer(auto_error=False)


def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    """Dépendance FastAPI : refuse la requête si le jeton Bearer est absent ou invalide."""
    if credentials is None or not secrets.compare_digest(
        credentials.credentials, API_TOKEN
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton absent ou invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
