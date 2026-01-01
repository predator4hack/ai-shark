from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
import io

from ..services.storage_manager import storage
from ..schemas.document import FileDownloadResponse

router = APIRouter(prefix="/api/v1/files", tags=["files"])


@router.get("/download/{company_name}/{file_path:path}")
async def download_file(company_name: str, file_path: str):
    """
    Download a processed file.
    For GCS: Returns redirect to signed URL
    For Local: Streams file directly
    """
    full_path = f"{company_name}/{file_path}"

    if not storage.file_exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    # For GCS, redirect to signed URL
    if hasattr(storage.backend, 'bucket_name'):
        signed_url = storage.get_download_url(full_path)
        return RedirectResponse(url=signed_url)

    # For local, stream file
    content = storage.read_file(full_path)
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_path.split('/')[-1]}"}
    )


@router.get("/{company_name}/list")
async def list_company_files(company_name: str):
    """List all files for a company"""
    files = storage.list_files(company_name)

    return {
        "company_name": company_name,
        "files": [
            {
                "path": f,
                "download_url": f"/api/v1/files/download/{f}"
            }
            for f in files
        ]
    }
