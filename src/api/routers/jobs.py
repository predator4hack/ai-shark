from fastapi import APIRouter, HTTPException

from ..schemas.document import JobStatusResponse
from ..services.job_manager import job_manager

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get current status of a processing job.
    Used for polling from React frontend.
    """
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        progress_message=job.progress_message,
        result=job.result,
        error=job.error
    )
