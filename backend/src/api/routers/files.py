from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response, RedirectResponse
from pathlib import Path
import logging
import os

from ..services.firestore_manager import firestore_db
from ..services.firebase_storage_manager import firebase_storage
from src.utils.output_manager import OutputManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/files", tags=["files"])

# Allowed file extensions for security
ALLOWED_EXTENSIONS = {'.md', '.pdf'}

# Base outputs directory
OUTPUTS_DIR = Path("outputs")


def get_company_id_from_name(company_name: str) -> str:
    """
    Generate company_id from company name using the same logic as Firestore.
    This is a temporary solution - ideally we'd have a mapping table.
    """
    # For now, we try to find the company by searching for metadata
    sanitized_name = OutputManager.sanitize_company_name(company_name)
    metadata_file = os.path.join(f"outputs/{sanitized_name}", "metadata.json")

    if os.path.exists(metadata_file):
        import json
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        website = metadata.get('website')
        if website:
            company = firestore_db.get_company_by_url(website)
            if company:
                return company['company_id']

    # Fallback: generate ID from a placeholder URL
    # This won't work in production, but helps during development
    import hashlib
    return hashlib.sha256(f"https://{company_name}.com".encode()).hexdigest()[:16]


@router.get("/{company_name}/founders-checklist.md")
async def get_founders_checklist(company_name: str):
    """Get founders checklist markdown"""

    # Try Firestore first
    if firestore_db.enabled:
        try:
            company_id = get_company_id_from_name(company_name)

            # Try to get questionnaire from Firestore
            # We don't know which agents were used, so try common combinations
            for agent_combo in [
                ['business', 'market', 'tech', 'risk'],  # All 4 agents
                ['business', 'market', 'tech'],           # 3 agents
                ['business', 'market'],                   # 2 agents
            ]:
                questionnaire = firestore_db.get_questionnaire(company_id, agent_combo)
                if questionnaire:
                    content = questionnaire['content']
                    return Response(content=content, media_type="text/markdown")
        except Exception as e:
            logger.warning(f"Failed to fetch from Firestore: {e}")

    # Fallback to local file
    sanitized_name = OutputManager.sanitize_company_name(company_name)
    file_path = Path(f"outputs/{sanitized_name}/founders-checklist.md")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Questionnaire not found")

    return FileResponse(
        path=str(file_path),
        filename="founders-checklist.md",
        media_type="text/markdown"
    )


@router.get("/{company_name}/founders-qa-responses.md")
async def get_qa_responses(company_name: str):
    """Get Q&A responses markdown"""

    # Try Firestore first
    if firestore_db.enabled:
        try:
            company_id = get_company_id_from_name(company_name)
            qa = firestore_db.get_qa_responses(company_id)

            if qa:
                content = qa['content']
                return Response(content=content, media_type="text/markdown")
        except Exception as e:
            logger.warning(f"Failed to fetch Q&A from Firestore: {e}")

    # Fallback to local file
    sanitized_name = OutputManager.sanitize_company_name(company_name)
    file_path = Path(f"outputs/{sanitized_name}/founders-qa-responses.md")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Q&A responses not found")

    return FileResponse(
        path=str(file_path),
        filename="founders-qa-responses.md",
        media_type="text/markdown"
    )


@router.get("/{company_name}/investment-memo.md")
async def get_investment_memo(company_name: str):
    """Get investment memo markdown"""

    # Try Firestore first
    if firestore_db.enabled:
        try:
            company_id = get_company_id_from_name(company_name)
            memo = firestore_db.get_memo(company_id)

            if memo:
                content = memo['content']
                return Response(content=content, media_type="text/markdown")
        except Exception as e:
            logger.warning(f"Failed to fetch memo from Firestore: {e}")

    # Fallback to local file
    sanitized_name = OutputManager.sanitize_company_name(company_name)
    file_path = Path(f"outputs/{sanitized_name}/investment-memo.md")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Investment memo not found")

    return FileResponse(
        path=str(file_path),
        filename="investment-memo.md",
        media_type="text/markdown"
    )


@router.get("/{company_name}/investment-memo.pdf")
async def get_investment_memo_pdf(company_name: str):
    """Get investment memo PDF (redirects to Firebase Storage)"""

    # Try Firebase Storage first
    if firebase_storage.enabled:
        try:
            sanitized_name = OutputManager.sanitize_company_name(company_name)
            pdf_url = firebase_storage.get_pdf_url(sanitized_name, "investment-memo.pdf")

            if pdf_url:
                # Return redirect to signed URL
                return RedirectResponse(url=pdf_url)
        except Exception as e:
            logger.warning(f"Failed to get PDF from Firebase Storage: {e}")

    # Fallback to local file
    sanitized_name = OutputManager.sanitize_company_name(company_name)
    file_path = Path(f"outputs/{sanitized_name}/investment-memo.pdf")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        path=str(file_path),
        filename="investment-memo.pdf",
        media_type="application/pdf"
    )


@router.get("/{company_name}/analysis/{agent_type}_analysis.md")
async def get_analysis_report(company_name: str, agent_type: str):
    """
    Get specific agent analysis report

    Args:
        agent_type: business | market | tech | risk
    """
    if agent_type not in ['business', 'market', 'tech', 'risk']:
        raise HTTPException(status_code=400, detail="Invalid agent type")

    # Try Firestore first
    if firestore_db.enabled:
        try:
            company_id = get_company_id_from_name(company_name)
            analysis = firestore_db.get_analysis(company_id, agent_type)

            if analysis:
                content = analysis['markdown_analysis']
                return Response(content=content, media_type="text/markdown")
        except Exception as e:
            logger.warning(f"Failed to fetch analysis from Firestore: {e}")

    # Fallback to local file
    sanitized_name = OutputManager.sanitize_company_name(company_name)
    file_path = Path(f"outputs/{sanitized_name}/analysis/{agent_type}_analysis.md")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"{agent_type} analysis not found")

    return FileResponse(
        path=str(file_path),
        filename=f"{agent_type}_analysis.md",
        media_type="text/markdown"
    )


@router.get("/download")
async def download_file(path: str = Query(..., description="Path to the file to download")):
    """
    Generic file download endpoint (legacy support)

    Query params:
        path: File path relative to outputs/ directory

    Security measures:
    - Only .md and .pdf files are allowed
    - Path must be within the outputs directory (prevents path traversal)
    """
    # Security: Prevent path traversal
    if ".." in path or path.startswith("/"):
        logger.warning(f"Attempted path traversal attack: {path}")
        raise HTTPException(status_code=400, detail="Invalid file path")

    file_path = Path(path)

    # Check file extension
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        logger.warning(f"Attempted to download file with disallowed extension: {path}")
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Only {', '.join(ALLOWED_EXTENSIONS)} files can be downloaded."
        )

    # Parse company name and file type from path
    # Example: "sia/founders-checklist.md" or "sia/investment-memo.pdf"
    parts = path.split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid path format")

    company_name = parts[0]
    filename = parts[-1]

    # Route to appropriate endpoint based on filename
    if filename == "founders-checklist.md":
        return await get_founders_checklist(company_name)
    elif filename == "founders-qa-responses.md":
        return await get_qa_responses(company_name)
    elif filename == "investment-memo.md":
        return await get_investment_memo(company_name)
    elif filename == "investment-memo.pdf":
        return await get_investment_memo_pdf(company_name)
    elif filename.endswith("_analysis.md"):
        # Extract agent type from filename (e.g., "business_analysis.md" -> "business")
        agent_type = filename.replace("_analysis.md", "")
        if "analysis/" in path:
            return await get_analysis_report(company_name, agent_type)

    # Fallback to local file for other files
    # Resolve the path to prevent path traversal attacks
    file_path = Path(f"outputs/{path}")

    # Ensure the file is within the outputs directory
    outputs_resolved = OUTPUTS_DIR.resolve()
    try:
        resolved_path = file_path.resolve()
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
