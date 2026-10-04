from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url

from app.nalashtuvannia.parametry import parametry


def build_database_url():
    if parametry.database_url:
        url = make_url(
            parametry.database_url
        )

        if url.drivername in {
            "postgres",
            "postgresql",
        }:
            url = url.set(
                drivername="postgresql+psycopg"
            )

        return url

    required = {
        "DB_HOST": parametry.db_host,
        "DB_PORT": parametry.db_port,
        "DB_NAME": parametry.db_name,
        "DB_USER": parametry.db_user,
        "DB_PASSWORD": parametry.db_password,
    }

    missing = [
        name
        for name, value
        in required.items()
        if value is None
    ]

    if missing:
        raise RuntimeError(
            "Database configuration is incomplete. "
            "Set DATABASE_URL or: "
            + ", ".join(missing)
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=parametry.db_user,
        password=parametry.db_password,
        host=parametry.db_host,
        port=parametry.db_port,
        database=parametry.db_name,
    )


adresa_bazy = build_database_url()


dvyhun_bazy = create_engine(
    adresa_bazy,
    pool_pre_ping=True,
    pool_recycle=300,
)
