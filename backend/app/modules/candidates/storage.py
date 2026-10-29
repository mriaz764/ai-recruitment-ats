import re
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

from app.core.config import RESUME_STORAGE_DIR

STORAGE_KEY_PATTERN = re.compile(r"^[0-9a-f]{32}\.(?:pdf|docx)$")
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class BaseStorageProvider(ABC):
    @abstractmethod
    def save_resume(self, content: bytes, extension: str, organization_id: int) -> str:
        pass

    @abstractmethod
    def get_resume_path(self, storage_key: str, organization_id: int) -> Path:
        pass

    @abstractmethod
    def delete_resume(self, storage_key: str, organization_id: int) -> None:
        pass


class LocalStorageProvider(BaseStorageProvider):
    def __init__(self, base_dir: Path = RESUME_STORAGE_DIR):
        self.base_dir = base_dir

    def _get_org_dir(self, organization_id: int) -> Path:
        org_dir = self.base_dir / f"org_{organization_id}"
        org_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        return org_dir

    def save_resume(self, content: bytes, extension: str, organization_id: int) -> str:
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("Unsupported resume extension.")

        org_dir = self._get_org_dir(organization_id)
        storage_key = f"{uuid4().hex}{extension}"
        destination = org_dir / storage_key

        with destination.open("xb") as file:
            file.write(content)

        return storage_key

    def get_resume_path(self, storage_key: str, organization_id: int) -> Path:
        if not STORAGE_KEY_PATTERN.fullmatch(storage_key):
            raise ValueError("Invalid resume storage key.")

        return self._get_org_dir(organization_id) / storage_key

    def delete_resume(self, storage_key: str, organization_id: int) -> None:
        path = self.get_resume_path(storage_key, organization_id)
        path.unlink(missing_ok=True)


# Default singleton instance
storage_provider = LocalStorageProvider()