import re
from pathlib import Path
from uuid import uuid4

from app.core.config import RESUME_STORAGE_DIR

STORAGE_KEY_PATTERN = re.compile(r"^[0-9a-f]{32}\.(?:pdf|docx)$")

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def save_resume(content: bytes, extension: str) -> str:
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported resume extension.")

    RESUME_STORAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
        mode=0o700,
    )

    storage_key = f"{uuid4().hex}{extension}"
    destination = RESUME_STORAGE_DIR / storage_key

    with destination.open("xb") as file:
        file.write(content)

    return storage_key


def get_resume_path(storage_key: str) -> Path:
    if not STORAGE_KEY_PATTERN.fullmatch(storage_key):
        raise ValueError("Invalid resume storage key.")

    return RESUME_STORAGE_DIR / storage_key


def delete_resume(storage_key: str) -> None:
    path = get_resume_path(storage_key)
    path.unlink(missing_ok=True)
