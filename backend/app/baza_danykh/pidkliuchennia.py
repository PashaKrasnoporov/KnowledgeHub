from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from app.nalashtuvannia.parametry import parametry


adresa_bazy = URL.create(
    drivername="postgresql+psycopg",
    username=parametry.db_user,
    password=parametry.db_password,
    host=parametry.db_host,
    port=parametry.db_port,
    database=parametry.db_name,
)


dvyhun_bazy = create_engine(
    adresa_bazy,
    pool_pre_ping=True,
)