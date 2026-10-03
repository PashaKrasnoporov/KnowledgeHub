from datetime import (
    datetime,
    timezone,
)

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.bezpeka.sesii import (
    SESSION_LIFETIME,
    generate_session_token,
    hash_session_token,
)
from app.modeli.user import User
from app.modeli.user_session import UserSession
from app.repositories.session_repository import (
    add_user_session,
    get_user_session_by_token_hash,
    revoke_user_session,
)
from app.repositories.user_repository import (
    get_user_by_id,
)


def create_user_session(
    session: Session,
    user: User,
) -> tuple[str, UserSession]:
    token = generate_session_token()

    token_hash = hash_session_token(
        token
    )

    now = datetime.now(
        timezone.utc
    )

    user_session = UserSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=(
            now
            + SESSION_LIFETIME
        ),
        revoked_at=None,
    )

    try:
        add_user_session(
            session=session,
            user_session=user_session,
        )

        session.commit()

        return (
            token,
            user_session,
        )

    except SQLAlchemyError:
        session.rollback()
        raise


def get_user_by_session_token(
    session: Session,
    session_token: str | None,
) -> User | None:
    if not session_token:
        return None

    token_hash = hash_session_token(
        session_token
    )

    user_session = (
        get_user_session_by_token_hash(
            session=session,
            token_hash=token_hash,
        )
    )

    if user_session is None:
        return None

    if user_session.revoked_at is not None:
        return None

    now = datetime.now(
        timezone.utc
    )

    if user_session.expires_at <= now:
        return None

    user = get_user_by_id(
        session=session,
        user_id=user_session.user_id,
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    return user


def revoke_session_by_token(
    session: Session,
    session_token: str | None,
) -> bool:
    if not session_token:
        return False

    token_hash = hash_session_token(
        session_token
    )

    user_session = (
        get_user_session_by_token_hash(
            session=session,
            token_hash=token_hash,
        )
    )

    if user_session is None:
        return False

    if user_session.revoked_at is not None:
        return True

    now = datetime.now(
        timezone.utc
    )

    try:
        revoke_user_session(
            session=session,
            user_session=user_session,
            revoked_at=now,
        )

        session.commit()

        return True

    except SQLAlchemyError:
        session.rollback()
        raise