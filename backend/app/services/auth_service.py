from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from app.bezpeka.paroli import (
    hash_password,
    verify_password_or_dummy,
)
from app.modeli.user import User
from app.repositories.user_repository import (
    add_user,
    get_user_by_email,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
)


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


def register_user(
    session: Session,
    user_data: UserCreate,
) -> User:
    name = user_data.name

    email = str(
        user_data.email
    )

    existing_user = get_user_by_email(
        session=session,
        email=email,
    )

    if existing_user is not None:
        raise EmailAlreadyExistsError(
            "User with this email already exists."
        )

    password_hash = hash_password(
        user_data.password
    )

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role="user",
        is_active=True,
    )

    try:
        add_user(
            session=session,
            user=user,
        )

        session.commit()

        return user

    except IntegrityError as exc:
        session.rollback()

        raise EmailAlreadyExistsError(
            "User with this email already exists."
        ) from exc

    except SQLAlchemyError:
        session.rollback()
        raise


def authenticate_user(
    session: Session,
    user_data: UserLogin,
) -> User:
    email = str(
        user_data.email
    )

    user = get_user_by_email(
        session=session,
        email=email,
    )

    stored_password_hash = (
        user.password_hash
        if user is not None
        else None
    )

    password_is_valid = (
        verify_password_or_dummy(
            password=user_data.password,
            hashed_password=stored_password_hash,
        )
    )

    if (
        user is None
        or not password_is_valid
    ):
        raise InvalidCredentialsError(
            "Invalid email or password."
        )

    if not user.is_active:
        raise InactiveUserError(
            "User account is inactive."
        )

    return user