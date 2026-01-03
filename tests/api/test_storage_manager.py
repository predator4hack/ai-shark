"""
Unit tests for storage manager (local and GCS backends)
"""
import pytest
from pathlib import Path
import io
from src.api.services.storage_manager import (
    LocalStorageBackend,
    StorageManager
)


class TestLocalStorageBackend:
    """Test cases for local filesystem storage backend"""

    def test_save_file_bytes(self, tmp_path):
        """Test saving file from bytes"""
        backend = LocalStorageBackend(base_dir=str(tmp_path))
        content = b"Test content for pitch deck"

        result_path = backend.save_file("test-company/pitch_deck.md", content)

        assert Path(result_path).exists()
        assert Path(result_path).read_bytes() == content

    def test_save_file_stream(self, tmp_path):
        """Test saving file from stream"""
        backend = LocalStorageBackend(base_dir=str(tmp_path))
        content = b"Test content from stream"
        stream = io.BytesIO(content)

        result_path = backend.save_file("test-company/data.json", stream)

        assert Path(result_path).exists()
        assert Path(result_path).read_bytes() == content

    def test_read_file(self, tmp_path):
        """Test reading file content"""
        backend = LocalStorageBackend(base_dir=str(tmp_path))
        content = b"Read this content"

        # First save
        backend.save_file("test-company/file.txt", content)

        # Then read
        read_content = backend.read_file("test-company/file.txt")
        assert read_content == content

    def test_file_exists(self, tmp_path):
        """Test checking file existence"""
        backend = LocalStorageBackend(base_dir=str(tmp_path))

        # Non-existent file
        assert not backend.file_exists("test-company/nonexistent.txt")

        # Create file
        backend.save_file("test-company/exists.txt", b"content")

        # Now it should exist
        assert backend.file_exists("test-company/exists.txt")

    def test_list_files(self, tmp_path):
        """Test listing files with prefix"""
        backend = LocalStorageBackend(base_dir=str(tmp_path))

        # Create multiple files
        backend.save_file("company-a/file1.md", b"content1")
        backend.save_file("company-a/file2.json", b"content2")
        backend.save_file("company-b/file3.md", b"content3")

        # List files for company-a
        files = backend.list_files("company-a")

        assert len(files) >= 2
        # Files should be relative paths
        assert any("file1.md" in f for f in files)
        assert any("file2.json" in f for f in files)

    def test_delete_file(self, tmp_path):
        """Test deleting a file"""
        backend = LocalStorageBackend(base_dir=str(tmp_path))

        # Create file
        backend.save_file("test-company/to_delete.txt", b"delete me")
        assert backend.file_exists("test-company/to_delete.txt")

        # Delete file
        backend.delete_file("test-company/to_delete.txt")
        assert not backend.file_exists("test-company/to_delete.txt")

    def test_get_download_url(self, tmp_path):
        """Test generating download URL for local storage"""
        backend = LocalStorageBackend(base_dir=str(tmp_path))

        # Create file
        backend.save_file("test-company/download.pdf", b"pdf content")

        # Get URL
        url = backend.get_download_url("test-company/download.pdf")

        # For local storage, should return relative API path
        assert "/api/v1/files/download/" in url
        assert "test-company/download.pdf" in url

    def test_nested_directory_creation(self, tmp_path):
        """Test automatic creation of nested directories"""
        backend = LocalStorageBackend(base_dir=str(tmp_path))

        # Save file in deeply nested path
        backend.save_file("company/phase1/documents/deck.pdf", b"content")

        # Verify file exists
        assert backend.file_exists("company/phase1/documents/deck.pdf")


class TestStorageManager:
    """Test cases for StorageManager (auto-detection logic)"""

    def test_storage_manager_local_mode(self, monkeypatch, tmp_path):
        """Test StorageManager defaults to local storage"""
        monkeypatch.setenv("USE_GCS", "false")
        monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))

        manager = StorageManager()

        # Should use LocalStorageBackend
        from src.api.services.storage_manager import LocalStorageBackend
        assert isinstance(manager.backend, LocalStorageBackend)

    def test_storage_manager_saves_file(self, monkeypatch, tmp_path):
        """Test that StorageManager can save files"""
        monkeypatch.setenv("USE_GCS", "false")
        monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))

        manager = StorageManager()
        content = b"Test via manager"

        result = manager.save_file("test-company/manager_test.txt", content)

        assert manager.file_exists("test-company/manager_test.txt")
        assert manager.read_file("test-company/manager_test.txt") == content


@pytest.mark.skipif(
    True,  # Skip by default (requires GCS credentials)
    reason="GCS tests require Google Cloud credentials"
)
class TestGCSStorageBackend:
    """Test cases for GCS storage backend (requires credentials)"""

    def test_gcs_save_and_read(self):
        """Test saving and reading from GCS"""
        from src.api.services.storage_manager import GCSStorageBackend

        # This test requires actual GCS credentials
        backend = GCSStorageBackend(bucket_name="ai-shark-test-bucket")

        content = b"Test GCS content"
        backend.save_file("test/gcs_file.txt", content)

        # Read back
        read_content = backend.read_file("test/gcs_file.txt")
        assert read_content == content

        # Cleanup
        backend.delete_file("test/gcs_file.txt")
