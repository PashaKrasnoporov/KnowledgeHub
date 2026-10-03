from sqlalchemy.orm import sessionmaker

from app.baza_danykh.pidkliuchennia import dvyhun_bazy


FabrykaSesii = sessionmaker(
    bind=dvyhun_bazy,
    autoflush=False,
    expire_on_commit=False,
)