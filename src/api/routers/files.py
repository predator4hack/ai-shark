from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter(prefix="/api/v1/files", tags=["files"])

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
