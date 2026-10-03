from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


DUMMY_PASSWORD_HASH = password_hash.hash(
    "KnowledgeHubDummyPassword"
)


def hash_password(
    password: str,
) -> str:
    return password_hash.hash(
        password
    )


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        password,
        hashed_password,
    )


def verify_password_or_dummy(
    password: str,
    hashed_password: str | None,
) -> bool:
    hash_to_check = (
        hashed_password
        if hashed_password is not None
        else DUMMY_PASSWORD_HASH
    )

    return password_hash.verify(
        password,
        hash_to_check,
    )