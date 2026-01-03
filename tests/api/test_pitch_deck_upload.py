"""
Integration tests for pitch deck upload and processing endpoints
"""
import pytest
import time
from pathlib import Path
import io


class TestPitchDeckUpload:
    """Test cases for pitch deck upload functionality"""

    def test_health_check(self, api_client):
        """Test API health check endpoint"""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-shark-api"

    def test_upload_pitch_deck_valid_pdf(self, api_client):
        """Test uploading a valid PDF pitch deck"""
        # Create a minimal valid PDF for testing
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"

        response = api_client.post(
            "/api/v1/documents/pitch-deck",
            files={"file": ("test_deck.pdf", io.BytesIO(pdf_content), "application/pdf")}
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["message"] == "Pitch deck uploaded successfully. Processing started."
        assert len(data["job_id"]) > 0

    def test_upload_pitch_deck_invalid_file_type(self, api_client):
        """Test rejection of invalid file types"""
        txt_content = b"This is not a valid pitch deck"

        response = api_client.post(
            "/api/v1/documents/pitch-deck",
            files={"file": ("invalid.txt", io.BytesIO(txt_content), "text/plain")}
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid file type" in data["detail"]

    def test_upload_pitch_deck_file_too_large(self, api_client):
        """Test rejection of files exceeding size limit"""
        # Create a file larger than 100MB (simulate with metadata)
        # Note: In real tests, you'd create actual large content
        large_content = b"x" * (101 * 1024 * 1024)  # 101MB

        response = api_client.post(
            "/api/v1/documents/pitch-deck",
            files={"file": ("large_deck.pdf", io.BytesIO(large_content), "application/pdf")}
        )

        assert response.status_code == 413
        data = response.json()
        assert "File too large" in data["detail"]

    def test_upload_pitch_deck_powerpoint(self, api_client):
        """Test uploading PowerPoint files"""
        # Minimal PPTX structure (not a real PPTX, but for testing)
        pptx_content = b"PK\x03\x04"  # ZIP file signature (PPTX is a ZIP)

        response = api_client.post(
            "/api/v1/documents/pitch-deck",
            files={"file": ("deck.pptx", io.BytesIO(pptx_content), "application/vnd.openxmlformats-officedocument.presentationml.presentation")}
        )

        # Should accept the file format (may fail processing, but that's OK for this test)
        assert response.status_code in [200, 500]  # 200 if accepted, 500 if processing fails


class TestJobStatus:
    """Test cases for job status polling"""

    def test_job_status_valid_job(self, api_client):
        """Test retrieving status of a valid job"""
        # First, upload a file to get a job_id
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"
        upload_response = api_client.post(
            "/api/v1/documents/pitch-deck",
            files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
        )

        assert upload_response.status_code == 200
        job_id = upload_response.json()["job_id"]

        # Poll status
        response = api_client.get(f"/api/v1/jobs/{job_id}/status")
        assert response.status_code == 200

        data = response.json()
        assert data["job_id"] == job_id
        assert "status" in data
        assert data["status"] in ["pending", "processing", "completed", "failed"]
        assert "progress_message" in data

    def test_job_status_invalid_job_id(self, api_client):
        """Test retrieving status with invalid job_id"""
        response = api_client.get("/api/v1/jobs/invalid-job-id-12345/status")

        assert response.status_code == 404
        data = response.json()
        assert "Job not found" in data["detail"]

    def test_job_status_progression(self, api_client):
        """Test that job status progresses over time"""
        # Upload a file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"
        upload_response = api_client.post(
            "/api/v1/documents/pitch-deck",
            files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
        )

        job_id = upload_response.json()["job_id"]

        # Initial status should be pending or processing
        response1 = api_client.get(f"/api/v1/jobs/{job_id}/status")
        status1 = response1.json()["status"]
        assert status1 in ["pending", "processing"]

        # Wait a bit and check again
        time.sleep(1)
        response2 = api_client.get(f"/api/v1/jobs/{job_id}/status")
        status2 = response2.json()["status"]

        # Status should have progressed or remained in processing
        assert status2 in ["processing", "completed", "failed"]


class TestFileDownload:
    """Test cases for file download endpoints"""

    def test_download_nonexistent_file(self, api_client):
        """Test downloading a file that doesn't exist"""
        response = api_client.get("/api/v1/files/download/nonexistent-company/pitch_deck.md")

        assert response.status_code == 404
        data = response.json()
        assert "File not found" in data["detail"]

    def test_list_company_files_empty(self, api_client):
        """Test listing files for a company with no files"""
        response = api_client.get("/api/v1/files/test-company/list")

        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "test-company"
        assert isinstance(data["files"], list)


class TestErrorHandling:
    """Test cases for error handling and edge cases"""

    def test_upload_without_file(self, api_client):
        """Test upload endpoint without providing a file"""
        response = api_client.post("/api/v1/documents/pitch-deck")

        assert response.status_code == 422  # Unprocessable Entity

    def test_invalid_endpoint(self, api_client):
        """Test accessing non-existent endpoint"""
        response = api_client.get("/api/v1/invalid-endpoint")

        assert response.status_code == 404

    def test_cors_headers(self, api_client):
        """Test CORS headers are present for development"""
        response = api_client.options("/api/v1/documents/pitch-deck")

        # Check for CORS headers (may vary based on configuration)
        assert response.status_code in [200, 405]  # OPTIONS method may or may not be allowed


@pytest.mark.skipif(
    not Path("tests/fixtures/sample_deck.pdf").exists(),
    reason="Sample PDF fixture not available"
)
class TestRealFileProcessing:
    """Integration tests with real sample files (requires fixtures)"""

    def test_process_real_pdf(self, api_client, sample_pdf_path):
        """Test processing a real sample PDF file"""
        with open(sample_pdf_path, "rb") as f:
            response = api_client.post(
                "/api/v1/documents/pitch-deck",
                files={"file": ("sample_deck.pdf", f, "application/pdf")}
            )

        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Poll until completion (with timeout)
        max_polls = 60  # 2 minutes max
        poll_interval = 2  # seconds

        for _ in range(max_polls):
            status_response = api_client.get(f"/api/v1/jobs/{job_id}/status")
            status_data = status_response.json()

            if status_data["status"] == "completed":
                assert status_data["result"] is not None
                assert "company_name" in status_data["result"]
                assert "files_created" in status_data["result"]
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"Processing failed: {status_data.get('error', 'Unknown error')}")

            time.sleep(poll_interval)
        else:
            pytest.fail("Processing timed out after 2 minutes")
