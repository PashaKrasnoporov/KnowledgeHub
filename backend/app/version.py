from pathlib import Path


_VERSION_FILE = (
    Path(__file__)
    .resolve()
    .parents[2]
    / "VERSION"
)

APP_VERSION = (
    _VERSION_FILE.read_text(encoding="utf-8").strip()
    if _VERSION_FILE.is_file()
    else "2.0.0"
)
