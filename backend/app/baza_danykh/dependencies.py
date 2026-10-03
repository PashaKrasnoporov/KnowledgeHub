from collections.abc import Generator

from sqlalchemy.orm import Session

from app.baza_danykh.sesii import FabrykaSesii


def get_db_session() -> Generator[
    Session,
    None,
    None,
]:
    session = FabrykaSesii()

    try:
        yield session

    finally:
        session.close()