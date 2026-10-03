import sys

from sqlalchemy import select

from app.baza_danykh.sesii import (
    FabrykaSesii,
)
from app.modeli.user import User


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage:"
        )

        print(
            "python -m scripts.set_admin "
            "user@example.com"
        )

        return

    email = (
        sys.argv[1]
        .strip()
        .lower()
    )

    session = FabrykaSesii()

    try:
        user = session.scalar(
            select(User)
            .where(
                User.email == email
            )
        )

        if user is None:
            print(
                f"User not found: {email}"
            )

            return

        user.role = "admin"
        user.is_active = True

        session.commit()

        print(
            "ADMIN CREATED"
        )

        print(
            f"ID: {user.id}"
        )

        print(
            f"Email: {user.email}"
        )

        print(
            f"Role: {user.role}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()
