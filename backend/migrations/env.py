from logging.config import fileConfig

from alembic import context

from app.baza_danykh.osnova_modelei import OsnovaModeli
from app.baza_danykh.pidkliuchennia import dvyhun_bazy

# Р†РјРїРѕСЂС‚СѓС”РјРѕ РјРѕРґРµР»С–, С‰РѕР± Alembic Р±Р°С‡РёРІ С—С… Сѓ metadata.
from app.modeli.user import User  # noqa: F401
from app.modeli.user_session import UserSession
from app.modeli.collection import Collection
from app.modeli.document import Document


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


from app.modeli.document_chunk import DocumentChunk

target_metadata = OsnovaModeli.metadata


def run_migrations_offline() -> None:
    url = dvyhun_bazy.url.render_as_string(
        hide_password=False,
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with dvyhun_bazy.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

