import os
from pathlib import Path


def _build_upload_root() -> Path:
    explicit = os.getenv(
        "UPLOAD_ROOT"
    )

    if explicit:
        return Path(
            explicit
        )

    railway_volume = os.getenv(
        "RAILWAY_VOLUME_MOUNT_PATH"
    )

    if railway_volume:
        return (
            Path(railway_volume)
            / "uploads"
        )

    return Path(
        "uploads"
    )


UPLOAD_ROOT = _build_upload_root()


MAX_FILE_SIZE = (
    10
    * 1024
    * 1024
)

FILE_CHUNK_SIZE = (
    1024
    * 1024
)


ALLOWED_FILE_TYPES = {
    ".pdf": {
        "application/pdf",
        "application/octet-stream",
    },

    ".docx": {
        (
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml.document"
        ),
        "application/zip",
        "application/octet-stream",
    },

    ".txt": {
        "text/plain",
        "application/octet-stream",
        "text/x-python",
        "text/x-log",
    },
}


class InvalidDocumentError(
    Exception
):
    pass


class DocumentTooLargeError(
    Exception
):
    pass


def validate_file_header(
    extension: str,
    first_chunk: bytes,
) -> None:
    if not first_chunk:
        raise InvalidDocumentError(
            "Файл порожній."
        )

    if extension == ".pdf":
        if not first_chunk.startswith(
            b"%PDF-"
        ):
            raise InvalidDocumentError(
                "Файл не є коректним PDF."
            )

        return


    if extension == ".docx":
        if not first_chunk.startswith(
            b"PK"
        ):
            raise InvalidDocumentError(
                "Файл не є коректним DOCX."
            )

        return


    if extension == ".txt":
        if b"\x00" in first_chunk:
            raise InvalidDocumentError(
                "TXT-файл містить "
                "бінарні дані."
            )

        try:
            first_chunk.decode(
                "utf-8-sig"
            )

        except UnicodeDecodeError:
            try:
                first_chunk.decode(
                    "cp1251"
                )

            except UnicodeDecodeError as exc:
                raise InvalidDocumentError(
                    "Не вдалося прочитати "
                    "TXT-файл як текст."
                ) from exc

        return


    raise InvalidDocumentError(
        "Непідтримуваний формат файла."
    )