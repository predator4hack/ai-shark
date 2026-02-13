from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class PitchDeckUploadResponse(BaseModel):
    job_id: str
    message: str = "Pitch deck upload started"


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress_message: str
    result: Optional[Dict] = None
    error: Optional[str] = None


class PitchDeckResult(BaseModel):
    success: bool
    company_name: str
    output_dir: str
    files_created: List[str]
    metadata: Dict
    processing_time: float


class FileDownloadResponse(BaseModel):
    filename: str
    download_url: str
    expires_in: int = 3600  # seconds
