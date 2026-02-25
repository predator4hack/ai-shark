"""
Storage abstraction for local filesystem.

⚠️ DEPRECATION NOTICE:
In cloud deployments (Cloud Run), use Firestore and Firebase Storage instead.
This storage manager is for local development and temporary file processing only.

For persistent storage:
- Text content (markdown): Use firestore_manager.py
- Binary files (PDFs): Use firebase_storage_manager.py
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional
import os


class StorageBackend(ABC):
    @abstractmethod
    def save_file(self, path: str, content: bytes | BinaryIO) -> str:
        """Save file and return public path/URL"""
        pass

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        """Read file content"""
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if file exists"""
        pass

    @abstractmethod
    def list_files(self, prefix: str) -> list[str]:
        """List files with given prefix"""
        pass

    @abstractmethod
    def delete_file(self, path: str) -> None:
        """Delete a file"""
        pass

    @abstractmethod
    def get_download_url(self, path: str, expiration: int = 3600) -> str:
        """Get download URL"""
        pass


class LocalStorageBackend(StorageBackend):
    """
    Local filesystem storage for development and temporary processing.

    ⚠️ Note: For production persistent storage, use:
    - firestore_manager for text content
    - firebase_storage_manager for binary files
    """

    def __init__(self, base_dir: str = "outputs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def save_file(self, path: str, content: bytes | BinaryIO) -> str:
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, bytes):
            full_path.write_bytes(content)
        else:
            with open(full_path, 'wb') as f:
                f.write(content.read())

        return str(full_path)

    def read_file(self, path: str) -> bytes:
        return (self.base_dir / path).read_bytes()

    def file_exists(self, path: str) -> bool:
        return (self.base_dir / path).exists()

    def list_files(self, prefix: str) -> list[str]:
        pattern = str(self.base_dir / prefix / "**/*")
        return [str(p.relative_to(self.base_dir)) for p in Path().glob(pattern) if p.is_file()]

    def delete_file(self, path: str) -> None:
        (self.base_dir / path).unlink(missing_ok=True)

    def get_download_url(self, path: str, expiration: int = 3600) -> str:
        # For local, return relative path
        return f"/api/v1/files/download/{path}"


class StorageManager:
    """
    Simplified storage manager for local file operations.

    ⚠️ DEPRECATION NOTICE:
    This manager is for temporary file processing and local development only.

    For production persistent storage on Cloud Run:
    - Text content (markdown, JSON): Use firestore_manager.py
    - Binary files (PDFs): Use firebase_storage_manager.py

    This storage manager is still used for:
    - Temporary files during document processing
    - Local development when USE_FIRESTORE=false
    - Intermediate files that don't need persistence
    """

    def __init__(self):
        # Always use local storage
        base_dir = os.getenv("OUTPUT_DIR", "outputs")
        self.backend = LocalStorageBackend(base_dir)
        print(f"ℹ️ Using local file storage: {base_dir}")
        print(f"ℹ️ For persistent storage, use firestore_manager and firebase_storage_manager")

    # Delegate all methods to backend
    def save_file(self, path: str, content: bytes | BinaryIO) -> str:
        return self.backend.save_file(path, content)

    def read_file(self, path: str) -> bytes:
        return self.backend.read_file(path)

    def file_exists(self, path: str) -> bool:
        return self.backend.file_exists(path)

    def list_files(self, prefix: str) -> list[str]:
        return self.backend.list_files(prefix)

    def delete_file(self, path: str) -> None:
        return self.backend.delete_file(path)

    def get_download_url(self, path: str, expiration: int = 3600) -> str:
        return self.backend.get_download_url(path, expiration)


# Global instance
storage = StorageManager()
