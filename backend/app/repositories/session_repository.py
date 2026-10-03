from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modeli.user_session import UserSession


def add_user_session(
    session: Session,
    user_session: UserSession,
) -> UserSession:
    session.add(
        user_session
    )

    session.flush()

    session.refresh(
        user_session
    )

    return user_session


def get_user_session_by_token_hash(
    session: Session,
    token_hash: str,
) -> UserSession | None:
    query = select(
        UserSession
    ).where(
        UserSession.token_hash
        == token_hash
    )

    return session.scalar(
        query
    )


def revoke_user_session(
    session: Session,
    user_session: UserSession,
    revoked_at: datetime,
) -> UserSession:
    user_session.revoked_at = revoked_at

    session.flush()

    session.refresh(
        user_session
    )

    return user_session