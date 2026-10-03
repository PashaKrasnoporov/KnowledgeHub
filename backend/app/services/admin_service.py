from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modeli.user import User
from app.repositories.admin_repository import (
    get_user_by_id,
)


class AdminActionError(Exception):
    pass


def change_user_active_status(
    session: Session,
    admin_user: User,
    target_user_id: int,
    is_active: bool,
) -> User | None:
    target_user = get_user_by_id(
        session=session,
        user_id=target_user_id,
    )

    if target_user is None:
        return None

    if (
        target_user.id
        == admin_user.id
        and not is_active
    ):
        raise AdminActionError(
            "????????????? ?? ???? "
            "???????????? ??????? ????????? ?????."
        )

    try:
        target_user.is_active = is_active

        session.commit()

        session.refresh(
            target_user
        )

        return target_user

    except SQLAlchemyError:
        session.rollback()
        raise
