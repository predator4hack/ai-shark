from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List
import time

from ..models.analysis import (
    RunAnalysisRequest,
    RunAnalysisResponse,
    DiscoverAgentsResponse,
    AgentInfo
)
from ..services.job_manager import job_manager, JobStatus
from src.processors.analysis_pipeline import AnalysisPipeline
from src.processors.questionnaire_processor import create_questionnaire_processor
from src.utils.output_manager import OutputManager

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


# Agent metadata for frontend (fixed list with 4 agents)
AGENT_METADATA = {
    "business": {
        "agent_name": "Business Analysis Agent",
        "description": "Analyzes business model, revenue streams, and financial projections"
    },
    "market": {
        "agent_name": "Market Analysis Agent",
        "description": "Evaluates market size, competition, and growth opportunities"
    },
    "tech": {
        "agent_name": "Technical Analysis Agent",
        "description": "Assesses technology stack, product architecture, and technical feasibility"
    },
    "risk": {
        "agent_name": "Risk Assessment Agent",
        "description": "Identifies potential risks, challenges, and mitigation strategies"
    }
}


def run_analysis_background(job_id: str, company_name: str, selected_agents: List[str]):
    """
    Background task to run multi-agent analysis.
    Updates job status throughout processing.
    """
    start_time = time.time()

    try:
        # Update: Starting analysis
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            f"Starting analysis with {len(selected_agents)} agents..."
        )

        # Sanitize company name for directory consistency
        sanitized_company_name = OutputManager.sanitize_company_name(company_name)
        company_dir = f"outputs/{sanitized_company_name}"

        # Initialize analysis pipeline
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Initializing analysis pipeline..."
        )

        pipeline = AnalysisPipeline(company_dir=company_dir)

        # Update: Running agents
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            f"Running {len(selected_agents)} selected agents..."
        )

        # Run selected agents
        analysis_results = pipeline.run_selected_agents(selected_agents)

        # Update: Generating reports
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Generating agent-specific reports..."
        )

        # Generate markdown reports for each agent
        pipeline.generate_agent_specific_reports(analysis_results)

        # Step 3: Generate questionnaire
        questionnaire_result = None
        try:
            job_manager.update_status(
                job_id,
                JobStatus.PROCESSING,
                "Generating founder questionnaire..."
            )

            questionnaire_processor = create_questionnaire_processor()
            questionnaire_result = questionnaire_processor.run_post_analysis_questionnaire(
                company_dir
            )

            if questionnaire_result.success:
                print(f"✅ Questionnaire generated: {questionnaire_result.markdown_file}")
            else:
                print(f"⚠️ Questionnaire generation failed: {questionnaire_result.error_message}")

        except Exception as e:
            print(f"❌ Questionnaire generation error: {e}")
            import traceback
            traceback.print_exc()
            questionnaire_result = None

        processing_time = time.time() - start_time

        # Count successful vs failed agents
        successful_count = sum(1 for r in analysis_results.values() if "error" not in r)
        failed_count = len(analysis_results) - successful_count

        # Build comprehensive result
        result = {
            "success": True,
            "company_name": company_name,
            "sanitized_company_name": sanitized_company_name,
            "selected_agents": selected_agents,
            "analysis_results": analysis_results,
            "successful_agents": successful_count,
            "failed_agents": failed_count,
            "processing_time": processing_time
        }

        # Add questionnaire result if available
        if questionnaire_result:
            import os
            file_size = 0
            if questionnaire_result.success and questionnaire_result.markdown_file:
                try:
                    file_size = os.path.getsize(questionnaire_result.markdown_file)
                except:
                    pass

            result["questionnaire"] = {
                "success": questionnaire_result.success,
                "markdown_file": questionnaire_result.markdown_file,
                "processing_time": questionnaire_result.processing_time,
                "error_message": questionnaire_result.error_message,
                "metadata": {
                    **questionnaire_result.metadata,
                    "file_size": file_size
                }
            }
        else:
            result["questionnaire"] = None

        # Update: Complete
        job_manager.update_status(
            job_id,
            JobStatus.COMPLETED,
            f"Analysis completed! {successful_count} agents successful, {failed_count} failed.",
            result=result
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error running multi-agent analysis: {error_details}")

        job_manager.update_status(
            job_id,
            JobStatus.FAILED,
            f"Analysis failed: {str(e)}",
            error=str(e)
        )


@router.get("/discover-agents", response_model=DiscoverAgentsResponse)
async def discover_agents():
    """
    Discover available analysis agents.
    Returns all 4 agent cards with availability status.
    """
    try:
        # Discover available agents without needing a company directory
        # Just check which factory functions exist
        import importlib
        import inspect
        from src import agents as agents_module

        # Get all agent factory functions
        available_agent_types = set()
        for name, obj in inspect.getmembers(agents_module):
            if callable(obj) and name.startswith('create_') and name.endswith('_agent'):
                # Extract agent type from function name: create_business_agent -> business
                agent_type = name.replace('create_', '').replace('_agent', '')
                available_agent_types.add(agent_type)

        # Build response with all 4 agents, marking availability
        agents = []
        for agent_type, metadata in AGENT_METADATA.items():
            agents.append(AgentInfo(
                agent_type=agent_type,
                agent_name=metadata["agent_name"],
                description=metadata["description"],
                available=(agent_type in available_agent_types)
            ))

        return DiscoverAgentsResponse(
            agents=agents,
            total_agents=len(agents),
            available_agents=len(available_agent_types)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to discover agents: {str(e)}"
        )


@router.post("/run-agents", response_model=RunAnalysisResponse)
async def run_agents(
    request: RunAnalysisRequest,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Run multi-agent analysis on selected agents.
    Returns job_id for status tracking.

    Requires Phase 1 (pitch deck upload) to be completed first.
    """

    # Validate request
    if not request.company_name or not request.company_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Company name is required"
        )

    if not request.selected_agents or len(request.selected_agents) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one agent must be selected"
        )

    # Validate that selected agents are valid
    valid_agent_types = set(AGENT_METADATA.keys())
    invalid_agents = [a for a in request.selected_agents if a not in valid_agent_types]

    if invalid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent types: {', '.join(invalid_agents)}. Valid types: {', '.join(valid_agent_types)}"
        )

    # Check if company directory exists (Phase 1 requirement)
    sanitized_company_name = OutputManager.sanitize_company_name(request.company_name)
    company_dir = f"outputs/{sanitized_company_name}"

    import os
    if not os.path.exists(company_dir):
        raise HTTPException(
            status_code=400,
            detail=f"Company directory not found. Please complete Phase 1 (pitch deck upload) first."
        )

    # Check if pitch_deck.md exists
    pitch_deck_file = os.path.join(company_dir, "pitch_deck.md")
    if not os.path.exists(pitch_deck_file):
        raise HTTPException(
            status_code=400,
            detail=f"Pitch deck not found for company '{request.company_name}'. Please upload pitch deck first."
        )

    # Create job
    job_id = job_manager.create_job()

    # Start background analysis
    background_tasks.add_task(
        run_analysis_background,
        job_id,
        request.company_name,
        request.selected_agents
    )

    return RunAnalysisResponse(
        job_id=job_id,
        message=f"Multi-agent analysis started with {len(request.selected_agents)} agents.",
        company_name=request.company_name,
        selected_agents=request.selected_agents
    )
