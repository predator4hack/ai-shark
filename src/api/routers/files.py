from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/files", tags=["files"])

# Allowed file extensions for security
ALLOWED_EXTENSIONS = {'.md', '.pdf'}

# Base outputs directory
OUTPUTS_DIR = Path("outputs")


@router.get("/download")
async def download_file(path: str = Query(..., description="Path to the file to download")):
    """
    Download a file by path query parameter.

    Security measures:
    - Only .md and .pdf files are allowed
    - Path must be within the outputs directory (prevents path traversal)
    """
    file_path = Path(path)

    # Check file extension
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        logger.warning(f"Attempted to download file with disallowed extension: {path}")
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Only {', '.join(ALLOWED_EXTENSIONS)} files can be downloaded."
        )

    # Resolve the path to prevent path traversal attacks
    # If path is relative (e.g., "outputs/company/file.md"), resolve it
    if not file_path.is_absolute():
        resolved_path = file_path.resolve()
    else:
        resolved_path = file_path

    # Ensure the file is within the outputs directory
    outputs_resolved = OUTPUTS_DIR.resolve()
    try:
        resolved_path.relative_to(outputs_resolved)
    except ValueError:
        logger.warning(f"Attempted path traversal attack: {path}")
        raise HTTPException(
            status_code=403,
            detail="Access denied. File must be within the outputs directory."
        )

    # Check if file exists
    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not resolved_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    # Determine media type based on extension
    media_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "text/markdown"

    return FileResponse(
        path=str(resolved_path),
        filename=file_path.name,
        media_type=media_type
    )


@router.get("/{company_name}/founders-checklist.md")
async def download_questionnaire(company_name: str):
    """Download the founders checklist for a company"""
    from src.utils.output_manager import OutputManager

    sanitized_name = OutputManager.sanitize_company_name(company_name)
    file_path = Path(f"outputs/{sanitized_name}/founders-checklist.md")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Questionnaire file not found")

    return FileResponse(
        path=str(file_path),
        filename="founders-checklist.md",
        media_type="text/markdown"
    )
