"""
Storage abstraction supporting both local filesystem and GCS.
Automatically detects environment and uses appropriate backend.
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
        """Get download URL (signed for GCS, direct for local)"""
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage for development"""

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


class GCSStorageBackend(StorageBackend):
    """Google Cloud Storage backend for production"""

    def __init__(self, bucket_name: str):
        from google.cloud import storage
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.bucket_name = bucket_name

    def save_file(self, path: str, content: bytes | BinaryIO) -> str:
        blob = self.bucket.blob(path)

        if isinstance(content, bytes):
            blob.upload_from_string(content)
        else:
            blob.upload_from_file(content, rewind=True)

        return f"gs://{self.bucket_name}/{path}"

    def read_file(self, path: str) -> bytes:
        blob = self.bucket.blob(path)
        return blob.download_as_bytes()

    def file_exists(self, path: str) -> bool:
        return self.bucket.blob(path).exists()

    def list_files(self, prefix: str) -> list[str]:
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        return [blob.name for blob in blobs]

    def delete_file(self, path: str) -> None:
        self.bucket.blob(path).delete()

    def get_download_url(self, path: str, expiration: int = 3600) -> str:
        blob = self.bucket.blob(path)
        return blob.generate_signed_url(expiration=expiration)


class StorageManager:
    """
    Main storage interface. Auto-detects environment:
    - Local: USE_GCS=false or missing
    - GCS: USE_GCS=true
    """

    def __init__(self):
        use_gcs = os.getenv("USE_GCS", "false").lower() == "true"

        if use_gcs:
            bucket_name = os.getenv("GCS_BUCKET_NAME", "ai-shark-outputs")
            self.backend = GCSStorageBackend(bucket_name)
            print(f"✅ Using GCS storage: {bucket_name}")
        else:
            base_dir = os.getenv("OUTPUT_DIR", "outputs")
            self.backend = LocalStorageBackend(base_dir)
            print(f"✅ Using local storage: {base_dir}")

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
