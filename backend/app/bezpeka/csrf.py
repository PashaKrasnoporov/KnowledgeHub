import secrets


CSRF_COOKIE_NAME = "knowledgehub_csrf"

CSRF_TOKEN_BYTES = 32

CSRF_COOKIE_MAX_AGE = 60 * 60


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(
        CSRF_TOKEN_BYTES
    )


def validate_csrf_token(
    form_token: str | None,
    cookie_token: str | None,
) -> bool:
    if not form_token:
        return False

    if not cookie_token:
        return False

    return secrets.compare_digest(
        form_token,
        cookie_token,
    )