from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modeli.user import User


def get_all_users(
    session: Session,
) -> list[User]:
    query = (
        select(User)
        .order_by(
            User.id.asc()
        )
    )

    return list(
        session.scalars(query).all()
    )


def get_user_by_id(
    session: Session,
    user_id: int,
) -> User | None:
    return session.get(
        User,
        user_id,
    )
