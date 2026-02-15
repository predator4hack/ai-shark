"""
Cache management API endpoints for Firestore-based caching.

Provides endpoints to:
- Check cache status for a company
- Invalidate cached analyses
- View cached analysis data
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, Dict, List
from pydantic import BaseModel

from ..services.firestore_manager import firestore_db

router = APIRouter(prefix="/api/v1/cache", tags=["cache"])


class CacheStatusResponse(BaseModel):
    """Response model for cache status"""
    exists: bool
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    website: Optional[str] = None
    cached_analyses: List[str] = []
    processing_status: Optional[Dict] = None
    last_updated: Optional[str] = None


class InvalidateCacheResponse(BaseModel):
    """Response model for cache invalidation"""
    message: str
    company_id: str
    invalidated_count: int


@router.get("/status", response_model=CacheStatusResponse)
async def get_cache_status(website: str = Query(..., description="Company website URL")):
    """
    Get cache status for a company by website URL.

    Returns information about cached analyses and processing status.

    Args:
        website: Company website URL (used as unique identifier)

    Returns:
        Cache status including list of cached analyses
    """
    if not firestore_db.enabled:
        raise HTTPException(
            status_code=503,
            detail="Firestore caching is not enabled. Set USE_FIRESTORE=true in environment."
        )

    try:
        company = firestore_db.get_company_by_url(website)

        if not company:
            return CacheStatusResponse(exists=False)

        # Get all analyses for this company
        cached_analyses = []
        for agent_type in ['business', 'market', 'tech', 'risk']:
            analysis = firestore_db.get_analysis(company['company_id'], agent_type)
            if analysis:
                cached_analyses.append(agent_type)

        return CacheStatusResponse(
            exists=True,
            company_id=company['company_id'],
            company_name=company.get('company_name'),
            website=website,
            cached_analyses=cached_analyses,
            processing_status=company.get('processing_status'),
            last_updated=str(company.get('updated_at')) if company.get('updated_at') else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache status: {str(e)}")


@router.post("/invalidate", response_model=InvalidateCacheResponse)
async def invalidate_cache(website: str = Query(..., description="Company website URL")):
    """
    Manually invalidate all cached analyses for a company.

    This will delete all cached analysis results, forcing them to be regenerated
    on the next analysis request.

    Args:
        website: Company website URL

    Returns:
        Confirmation message and number of invalidated analyses
    """
    if not firestore_db.enabled:
        raise HTTPException(
            status_code=503,
            detail="Firestore caching is not enabled. Set USE_FIRESTORE=true in environment."
        )

    try:
        company = firestore_db.get_company_by_url(website)

        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company not found with website: {website}"
            )

        company_id = company['company_id']

        # Count existing analyses before invalidation
        cached_count = 0
        for agent_type in ['business', 'market', 'tech', 'risk']:
            if firestore_db.get_analysis(company_id, agent_type):
                cached_count += 1

        # Invalidate all analyses
        firestore_db.invalidate_analyses(company_id)

        return InvalidateCacheResponse(
            message="Cache invalidated successfully",
            company_id=company_id,
            invalidated_count=cached_count
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to invalidate cache: {str(e)}")


@router.get("/analysis/{agent_type}")
async def get_cached_analysis(
    agent_type: str = Path(..., description="Agent type (business, market, tech, risk)"),
    website: str = Query(..., description="Company website URL")
):
    """
    Get a specific cached analysis for a company.

    Args:
        website: Company website URL
        agent_type: Type of analysis (business, market, tech, risk)

    Returns:
        Cached analysis data if available
    """
    if not firestore_db.enabled:
        raise HTTPException(
            status_code=503,
            detail="Firestore caching is not enabled. Set USE_FIRESTORE=true in environment."
        )

    valid_agent_types = ['business', 'market', 'tech', 'risk']
    if agent_type not in valid_agent_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent type. Must be one of: {', '.join(valid_agent_types)}"
        )

    try:
        company = firestore_db.get_company_by_url(website)

        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company not found with website: {website}"
            )

        analysis = firestore_db.get_analysis(company['company_id'], agent_type)

        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No cached {agent_type} analysis found for this company"
            )

        return {
            "company_id": company['company_id'],
            "company_name": company.get('company_name'),
            "agent_type": agent_type,
            "analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cached analysis: {str(e)}")


@router.get("/companies")
async def list_companies(limit: int = Query(50, ge=1, le=100)):
    """
    List all companies in Firestore cache.

    This is a debug endpoint to see what companies have been cached.

    Args:
        limit: Maximum number of companies to return (1-100)

    Returns:
        List of companies with their cache status
    """
    if not firestore_db.enabled:
        raise HTTPException(
            status_code=503,
            detail="Firestore caching is not enabled. Set USE_FIRESTORE=true in environment."
        )

    try:
        # Note: This requires implementing a list_companies method in FirestoreBackend
        # For now, return a helpful message
        return {
            "message": "This endpoint requires additional implementation in FirestoreBackend",
            "note": "To list companies, query the 'companies' collection directly in Firestore console"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list companies: {str(e)}")
