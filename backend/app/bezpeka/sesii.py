import hashlib
import secrets
from datetime import timedelta


SESSION_COOKIE_NAME = "knowledgehub_session"

SESSION_TOKEN_BYTES = 32

SESSION_LIFETIME = timedelta(
    days=7,
)


def generate_session_token() -> str:
    return secrets.token_urlsafe(
        SESSION_TOKEN_BYTES
    )


def hash_session_token(
    token: str,
) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()