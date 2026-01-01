from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
import time

from ..schemas.document import PitchDeckUploadResponse, PitchDeckResult
from ..services.job_manager import job_manager, JobStatus
from ..services.storage_manager import storage
from src.processors.pitch_deck_processor import PitchDeckProcessor

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


def process_pitch_deck_background(job_id: str, temp_file_path: str):
    """
    Background task to process pitch deck.
    Updates job status throughout processing.
    """
    start_time = time.time()

    try:
        # Update: Starting processing
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Starting pitch deck processing..."
        )

        # Initialize processor
        processor = PitchDeckProcessor()

        # Update: Converting to images
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Converting pitch deck to images..."
        )

        # Process pitch deck (existing logic)
        # Create a temporary output directory
        temp_output_dir = tempfile.mkdtemp()

        result = processor.process(
            file_path=temp_file_path,
            output_dir=temp_output_dir
        )

        # Get company name from result
        company_name = result.get("company_name", "unknown")

        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Saving processed files to storage..."
        )

        # Read and save files to storage
        files_created = []

        # Save pitch_deck.md to storage
        for created_file in result.get('files_created', []):
            if os.path.exists(created_file):
                # Read file content
                with open(created_file, 'rb') as f:
                    content = f.read()

                # Determine relative path for storage
                filename = os.path.basename(created_file)
                storage_path = f"{company_name}/{filename}"

                # Save to storage
                storage.save_file(storage_path, content)
                files_created.append(storage_path)

        # Clean up temp files
        import shutil
        shutil.rmtree(temp_output_dir, ignore_errors=True)

        processing_time = time.time() - start_time

        # Update: Complete
        job_manager.update_status(
            job_id,
            JobStatus.COMPLETED,
            "Pitch deck processing completed!",
            result={
                "success": True,
                "company_name": company_name,
                "files_created": files_created,
                "metadata": result.get('metadata', {}),
                "processing_time": processing_time
            }
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing pitch deck: {error_details}")

        job_manager.update_status(
            job_id,
            JobStatus.FAILED,
            f"Processing failed: {str(e)}",
            error=str(e)
        )

    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/pitch-deck", response_model=PitchDeckUploadResponse)
async def upload_pitch_deck(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload and process pitch deck (PDF/PPT/PPTX).
    Returns job_id for status tracking.

    File size limit: 100MB
    """

    # Validate file type
    allowed_extensions = [".pdf", ".ppt", ".pptx"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Validate file size (100MB limit)
    MAX_SIZE = 100 * 1024 * 1024  # 100MB in bytes
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: 100MB"
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    # Create job
    job_id = job_manager.create_job()

    # Start background processing
    background_tasks.add_task(process_pitch_deck_background, job_id, temp_path)

    return PitchDeckUploadResponse(
        job_id=job_id,
        message="Pitch deck uploaded successfully. Processing started."
    )
