"""
Persistent job tracking for async processing.
Stores job status, progress messages, and results in GCS/local storage and Firestore.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel
import uuid
import logging
import os

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    job_id: str
    status: JobStatus
    progress_message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    company_name: Optional[str] = None


class JobManager:
    """
    Persistent job store using GCS/local storage and Firestore.
    Jobs stored as JSON files at: _jobs/{job_id}.json
    And optionally in Firestore for better querying.
    """
    JOB_PREFIX = "_jobs"

    def __init__(self, storage, firestore_db=None):
        """
        Initialize JobManager with storage and optional Firestore backend.

        Args:
            storage: StorageManager instance (supports both local and GCS)
            firestore_db: FirestoreManager instance (optional)
        """
        self.storage = storage
        self.firestore_db = firestore_db
        self.use_firestore = firestore_db and firestore_db.enabled

    def _job_path(self, job_id: str) -> str:
        """Get the storage path for a job."""
        return f"{self.JOB_PREFIX}/{job_id}.json"

    def create_job(self, company_name: Optional[str] = None) -> str:
        """Create new job and return job_id"""
        job_id = str(uuid.uuid4())
        now = datetime.utcnow()

        job = Job(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress_message="Job created, waiting to start...",
            created_at=now,
            updated_at=now,
            company_name=company_name
        )

        # Persist to storage (file-based)
        self._save_job(job)

        # Also save to Firestore if enabled
        if self.use_firestore:
            try:
                self.firestore_db.save_job(job.model_dump(mode='json'))
                logger.info(f"Created job {job_id} in Firestore")
            except Exception as e:
                logger.warning(f"Failed to save job to Firestore: {e}")

        logger.info(f"Created job {job_id} in persistent storage")
        return job_id

    def _save_job(self, job: Job) -> None:
        """Save job to persistent storage."""
        try:
            job_json = job.model_dump_json()
            self.storage.save_file(self._job_path(job.job_id), job_json.encode())
        except Exception as e:
            logger.error(f"Failed to save job {job.job_id}: {e}")
            raise

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        progress_message: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Update job status and progress"""
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Update fields
        job.status = status
        job.progress_message = progress_message
        job.updated_at = datetime.utcnow()

        if result is not None:
            job.result = result
        if error is not None:
            job.error = error

        # Persist changes to file storage
        self._save_job(job)

        # Also update in Firestore if enabled
        if self.use_firestore:
            try:
                updates = {
                    "status": status.value,
                    "progress_message": progress_message,
                    "updated_at": datetime.utcnow()
                }
                if result is not None:
                    updates["result"] = result
                if error is not None:
                    updates["error"] = error

                self.firestore_db.update_job(job_id, updates)
            except Exception as e:
                logger.warning(f"Failed to update job in Firestore: {e}")

        logger.debug(f"Updated job {job_id}: {status.value} - {progress_message}")

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID from persistent storage (try Firestore first, then file storage)"""
        # Try Firestore first if enabled
        if self.use_firestore:
            try:
                job_data = self.firestore_db.get_job(job_id)
                if job_data:
                    return Job(**job_data)
            except Exception as e:
                logger.debug(f"Failed to get job from Firestore: {e}")

        # Fallback to file-based storage
        try:
            data = self.storage.read_file(self._job_path(job_id))
            return Job.model_validate_json(data)
        except Exception as e:
            logger.debug(f"Job {job_id} not found: {e}")
            return None

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove jobs older than max_age_hours"""
        try:
            job_files = self.storage.list_files(self.JOB_PREFIX)
            now = datetime.utcnow()
            deleted_count = 0

            for job_path in job_files:
                if not job_path.endswith('.json'):
                    continue

                job_id = job_path.split('/')[-1].replace('.json', '')
                job = self.get_job(job_id)

                if job and (now - job.created_at).total_seconds() > max_age_hours * 3600:
                    self.storage.delete_file(job_path)
                    deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old jobs")
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")


# Import storage and firestore, create global instance
from src.api.services.storage_manager import storage
from src.api.services.firestore_manager import firestore_db

job_manager = JobManager(storage, firestore_db)
