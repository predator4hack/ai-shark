"""
In-memory job tracking for async processing.
Stores job status, progress messages, and results.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel
import uuid


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
    Simple in-memory job store.
    For production, consider Redis or database.
    """

    def __init__(self):
        self._jobs: Dict[str, Job] = {}

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

        self._jobs[job_id] = job
        return job_id

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        progress_message: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Update job status and progress"""
        if job_id not in self._jobs:
            raise ValueError(f"Job {job_id} not found")

        job = self._jobs[job_id]
        job.status = status
        job.progress_message = progress_message
        job.updated_at = datetime.utcnow()

        if result:
            job.result = result
        if error:
            job.error = error

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self._jobs.get(job_id)

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove jobs older than max_age_hours"""
        now = datetime.utcnow()
        to_delete = [
            job_id for job_id, job in self._jobs.items()
            if (now - job.created_at).total_seconds() > max_age_hours * 3600
        ]
        for job_id in to_delete:
            del self._jobs[job_id]


# Global instance
job_manager = JobManager()
