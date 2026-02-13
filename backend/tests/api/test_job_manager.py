"""
Unit tests for job manager service
"""
import pytest
from datetime import datetime, timedelta
from src.api.services.job_manager import JobManager, JobStatus, Job


class TestJobManager:
    """Test cases for job management functionality"""

    def test_create_job(self):
        """Test creating a new job"""
        manager = JobManager()

        job_id = manager.create_job(company_name="TestCo")

        assert job_id is not None
        assert len(job_id) > 0

        # Verify job was created
        job = manager.get_job(job_id)
        assert job is not None
        assert job.job_id == job_id
        assert job.status == JobStatus.PENDING
        assert job.company_name == "TestCo"

    def test_create_job_without_company_name(self):
        """Test creating job without company name"""
        manager = JobManager()

        job_id = manager.create_job()

        job = manager.get_job(job_id)
        assert job.company_name is None

    def test_update_job_status(self):
        """Test updating job status and progress"""
        manager = JobManager()
        job_id = manager.create_job()

        # Update to processing
        manager.update_status(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress_message="Processing pitch deck..."
        )

        job = manager.get_job(job_id)
        assert job.status == JobStatus.PROCESSING
        assert job.progress_message == "Processing pitch deck..."

    def test_update_job_with_result(self):
        """Test updating job with result data"""
        manager = JobManager()
        job_id = manager.create_job()

        result_data = {
            "company_name": "TestCo",
            "files_created": ["pitch_deck.md", "metadata.json"],
            "processing_time": 45.2
        }

        manager.update_status(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            progress_message="Processing complete",
            result=result_data
        )

        job = manager.get_job(job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.result == result_data
        assert job.result["company_name"] == "TestCo"

    def test_update_job_with_error(self):
        """Test updating job with error"""
        manager = JobManager()
        job_id = manager.create_job()

        error_msg = "Failed to process PDF: Invalid format"

        manager.update_status(
            job_id=job_id,
            status=JobStatus.FAILED,
            progress_message="Processing failed",
            error=error_msg
        )

        job = manager.get_job(job_id)
        assert job.status == JobStatus.FAILED
        assert job.error == error_msg

    def test_update_nonexistent_job(self):
        """Test updating a job that doesn't exist"""
        manager = JobManager()

        with pytest.raises(ValueError, match="Job .* not found"):
            manager.update_status(
                job_id="nonexistent-job-id",
                status=JobStatus.COMPLETED,
                progress_message="This should fail"
            )

    def test_get_nonexistent_job(self):
        """Test getting a job that doesn't exist"""
        manager = JobManager()

        job = manager.get_job("nonexistent-job-id")
        assert job is None

    def test_job_timestamps(self):
        """Test that job timestamps are set correctly"""
        manager = JobManager()
        before_create = datetime.utcnow()

        job_id = manager.create_job()

        after_create = datetime.utcnow()

        job = manager.get_job(job_id)
        assert before_create <= job.created_at <= after_create
        assert job.created_at == job.updated_at

        # Update job and check timestamp changes
        import time
        time.sleep(0.1)  # Ensure time difference

        manager.update_status(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress_message="Processing..."
        )

        updated_job = manager.get_job(job_id)
        assert updated_job.updated_at > updated_job.created_at

    def test_cleanup_old_jobs(self):
        """Test cleaning up old jobs"""
        manager = JobManager()

        # Create a job
        job_id = manager.create_job()

        # Manually set created_at to 25 hours ago
        job = manager.get_job(job_id)
        job.created_at = datetime.utcnow() - timedelta(hours=25)

        # Cleanup jobs older than 24 hours
        manager.cleanup_old_jobs(max_age_hours=24)

        # Job should be deleted
        assert manager.get_job(job_id) is None

    def test_cleanup_preserves_recent_jobs(self):
        """Test that cleanup doesn't delete recent jobs"""
        manager = JobManager()

        # Create a recent job
        job_id = manager.create_job()

        # Cleanup old jobs
        manager.cleanup_old_jobs(max_age_hours=24)

        # Recent job should still exist
        assert manager.get_job(job_id) is not None

    def test_multiple_jobs(self):
        """Test managing multiple jobs simultaneously"""
        manager = JobManager()

        # Create multiple jobs
        job_ids = []
        for i in range(5):
            job_id = manager.create_job(company_name=f"Company{i}")
            job_ids.append(job_id)

        # Verify all jobs exist
        for job_id in job_ids:
            assert manager.get_job(job_id) is not None

        # Update each job to different statuses
        statuses = [
            JobStatus.PENDING,
            JobStatus.PROCESSING,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.PROCESSING
        ]

        for job_id, status in zip(job_ids, statuses):
            manager.update_status(
                job_id=job_id,
                status=status,
                progress_message=f"Status: {status.value}"
            )

        # Verify all updates
        for job_id, expected_status in zip(job_ids, statuses):
            job = manager.get_job(job_id)
            assert job.status == expected_status

    def test_job_status_enum_values(self):
        """Test that JobStatus enum has correct values"""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.PROCESSING.value == "processing"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"

    def test_job_model_validation(self):
        """Test Job model Pydantic validation"""
        now = datetime.utcnow()

        job = Job(
            job_id="test-123",
            status=JobStatus.PENDING,
            progress_message="Test message",
            created_at=now,
            updated_at=now
        )

        assert job.job_id == "test-123"
        assert job.status == JobStatus.PENDING
        assert job.result is None
        assert job.error is None
        assert job.company_name is None
