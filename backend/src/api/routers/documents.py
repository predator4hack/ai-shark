from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import tempfile
import os
import time
import asyncio
import json

from ..schemas.document import PitchDeckUploadResponse, PitchDeckResult
from ..services.job_manager import job_manager, JobStatus
from ..services.storage_manager import storage
from ..services.firestore_manager import firestore_db
from src.processors.pitch_deck_processor import PitchDeckProcessor
from src.utils.progress_callback import ProgressCallback

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
        print(f"📋 Processing job {job_id} started")

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

        print(f"🔄 Starting pitch deck processing for job {job_id}")
        result = processor.process(
            file_path=temp_file_path,
            output_dir=temp_output_dir
        )

        # Check if processing failed
        if result.get('status') == 'error':
            raise Exception(result.get('error', 'Unknown error during processing'))

        # Get company name from result and sanitize it for directory naming
        raw_company_name = result.get("company_name", "unknown")
        from src.utils.output_manager import OutputManager
        company_name = OutputManager.sanitize_company_name(raw_company_name)

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
        # Add both raw and sanitized company names to metadata
        metadata = result.get('metadata', {})
        metadata['sanitized_company_name'] = company_name
        if 'startup_name' in metadata:
            metadata['raw_startup_name'] = metadata['startup_name']

        # Save to Firestore if enabled
        if firestore_db.enabled:
            try:
                website = metadata.get('website', '')
                if website:
                    # Create/update company in Firestore
                    company_id = firestore_db.save_company({
                        "company_name": metadata.get('startup_name', company_name),
                        "website": website,
                        "sector": metadata.get('sector', ''),
                        "sub_sector": metadata.get('sub_sector', ''),
                        "table_of_contents": metadata.get('table_of_contents', {})
                    })

                    # Save pitch deck content to Firestore
                    pitch_deck_path = f"{company_name}/pitch_deck.md"
                    if pitch_deck_path in files_created:
                        # Read the content from storage
                        content = storage.read_file(pitch_deck_path).decode('utf-8')

                        firestore_db.save_source_document(company_id, 'pitch_deck', content, {
                            "total_pages": metadata.get('total_pages'),
                            "original_filename": metadata.get('original_filename', ''),
                            "file_extension": metadata.get('file_extension', '')
                        })
                        print(f"✅ Saved pitch deck to Firestore for company {company_id}")
                else:
                    print("⚠️ No website URL in metadata, skipping Firestore save")
            except Exception as e:
                print(f"⚠️ Failed to save to Firestore: {e}")
                # Don't fail the entire process if Firestore save fails

        job_manager.update_status(
            job_id,
            JobStatus.COMPLETED,
            "Pitch deck processing completed!",
            result={
                "success": True,
                "company_name": company_name,  # This is the sanitized version
                "files_created": files_created,
                "metadata": metadata,
                "processing_time": processing_time
            }
        )

    except Exception as e:
        import traceback
        import sys
        error_details = traceback.format_exc()

        # Print to stderr to ensure it appears in Cloud Run logs
        print(f"❌ ERROR processing pitch deck (job {job_id}):", file=sys.stderr)
        print(f"❌ Exception type: {type(e).__name__}", file=sys.stderr)
        print(f"❌ Exception message: {str(e)}", file=sys.stderr)
        print(f"❌ Full traceback:\n{error_details}", file=sys.stderr)

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


async def pitch_deck_sse_generator(job_id: str, temp_file_path: str):
    """
    SSE generator for streaming pitch deck processing progress.
    Keeps HTTP connection alive to prevent Cloud Run CPU throttling.
    """

    def format_sse(event_type: str, data: dict) -> str:
        """Format data as Server-Sent Event"""
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    start_time = time.time()

    try:
        # Update job status: Starting
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Starting pitch deck processing..."
        )

        yield format_sse("progress", {
            "stage": "initializing",
            "message": "Starting pitch deck processing...",
            "progress": None
        })

        # Initialize processor with callback
        processor = PitchDeckProcessor()
        progress_callback = ProgressCallback()
        temp_output_dir = tempfile.mkdtemp()

        # Start processing in thread pool (allows async iteration)
        process_task = asyncio.create_task(
            asyncio.to_thread(
                processor.process_with_callback,
                temp_file_path,
                temp_output_dir,
                progress_callback
            )
        )

        # Stream progress events as they arrive
        async for progress in progress_callback.listen():
            yield format_sse("progress", {
                "stage": progress["type"],
                "message": progress["message"],
                "progress": {
                    "current": progress["current"],
                    "total": progress["total"],
                    "percent": int((progress["current"] / progress["total"]) * 100) if progress["current"] and progress["total"] else 0
                } if progress["current"] and progress["total"] else None
            })

            # Update job status with progress
            job_manager.update_status(
                job_id,
                JobStatus.PROCESSING,
                progress["message"]
            )

        # Wait for processing to complete
        result = await process_task

        # Check if processing failed
        if result.get('status') == 'error':
            raise Exception(result.get('error', 'Unknown error during processing'))

        # Save files to storage (same logic as background task)
        yield format_sse("progress", {
            "stage": "saving_files",
            "message": "Saving processed files to storage...",
            "progress": None
        })

        # Get company name from result and sanitize it
        raw_company_name = result.get("company_name", "unknown")
        from src.utils.output_manager import OutputManager
        company_name = OutputManager.sanitize_company_name(raw_company_name)

        # Save files to storage
        files_created = []
        for created_file in result.get('files_created', []):
            if os.path.exists(created_file):
                with open(created_file, 'rb') as f:
                    content = f.read()

                filename = os.path.basename(created_file)
                storage_path = f"{company_name}/{filename}"
                storage.save_file(storage_path, content)
                files_created.append(storage_path)

        # Clean up temp files
        import shutil
        shutil.rmtree(temp_output_dir, ignore_errors=True)

        # Save to Firestore if enabled
        metadata = result.get('metadata', {})
        metadata['sanitized_company_name'] = company_name
        if 'startup_name' in metadata:
            metadata['raw_startup_name'] = metadata['startup_name']

        if firestore_db.enabled:
            try:
                website = metadata.get('website', '')
                if website:
                    company_id = firestore_db.save_company({
                        "company_name": metadata.get('startup_name', company_name),
                        "website": website,
                        "sector": metadata.get('sector', ''),
                        "sub_sector": metadata.get('sub_sector', ''),
                        "table_of_contents": metadata.get('table_of_contents', {})
                    })

                    pitch_deck_path = f"{company_name}/pitch_deck.md"
                    if pitch_deck_path in files_created:
                        content = storage.read_file(pitch_deck_path).decode('utf-8')
                        firestore_db.save_source_document(company_id, 'pitch_deck', content, {
                            "total_pages": metadata.get('total_pages'),
                            "original_filename": metadata.get('original_filename', ''),
                            "file_extension": metadata.get('file_extension', '')
                        })
                        print(f"✅ Saved pitch deck to Firestore for company {company_id}")
            except Exception as e:
                print(f"⚠️ Failed to save to Firestore: {e}")

        processing_time = time.time() - start_time

        # Mark job as completed
        job_manager.update_status(
            job_id,
            JobStatus.COMPLETED,
            "Pitch deck processing completed!",
            result={
                "success": True,
                "company_name": company_name,
                "files_created": files_created,
                "metadata": metadata,
                "processing_time": processing_time
            }
        )

        # Send completion event
        yield format_sse("complete", {
            "job_id": job_id,
            "result": {
                "success": True,
                "company_name": company_name,
                "files_created": files_created,
                "metadata": metadata,
                "processing_time": processing_time
            }
        })

    except Exception as e:
        import traceback
        import sys
        error_details = traceback.format_exc()

        print(f"❌ ERROR processing pitch deck (job {job_id}):", file=sys.stderr)
        print(f"❌ Exception type: {type(e).__name__}", file=sys.stderr)
        print(f"❌ Exception message: {str(e)}", file=sys.stderr)
        print(f"❌ Full traceback:\n{error_details}", file=sys.stderr)

        job_manager.update_status(
            job_id,
            JobStatus.FAILED,
            f"Processing failed: {str(e)}",
            error=str(e)
        )

        yield format_sse("error", {
            "job_id": job_id,
            "error": str(e),
            "stage": "processing"
        })

    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/pitch-deck/stream")
async def upload_pitch_deck_sse(file: UploadFile = File(...)):
    """
    Upload and process pitch deck with SSE streaming (RECOMMENDED for Cloud Run).
    Streams real-time progress updates during processing.

    This endpoint keeps the HTTP connection alive during processing,
    preventing Cloud Run CPU throttling issues that occur with background tasks.

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

    # Return SSE streaming response
    return StreamingResponse(
        pitch_deck_sse_generator(job_id, temp_path),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )
