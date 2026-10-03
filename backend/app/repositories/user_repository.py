from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modeli.user import User


def get_user_by_id(
    session: Session,
    user_id: int,
) -> User | None:
    query = select(
        User
    ).where(
        User.id == user_id
    )

    return session.scalar(
        query
    )


def get_user_by_email(
    session: Session,
    email: str,
) -> User | None:
    query = select(
        User
    ).where(
        User.email == email
    )

    return session.scalar(
        query
    )


def add_user(
    session: Session,
    user: User,
) -> User:
    session.add(
        user
    )

    session.flush()

    session.refresh(
        user
    )

    return user