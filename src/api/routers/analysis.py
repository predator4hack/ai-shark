from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form
from typing import List
import time
import os
import shutil

from ..models.analysis import (
    RunAnalysisRequest,
    RunAnalysisResponse,
    DiscoverAgentsResponse,
    AgentInfo,
    SimulateQARequest,
    GenerateMemoRequest,
    GenerateMemoResponse
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


def run_simulation_background(job_id: str, company_name: str):
    """
    Background task to run AI Q&A simulation.
    Uses questionnaire from Phase 3 and analysis reports as reference.
    """
    start_time = time.time()

    try:
        # Update: Starting simulation
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Starting Q&A simulation..."
        )

        # Sanitize company name for directory consistency
        sanitized_company_name = OutputManager.sanitize_company_name(company_name)
        company_dir = f"outputs/{sanitized_company_name}"

        # Check prerequisites
        checklist_path = os.path.join(company_dir, "founders-checklist.md")
        if not os.path.exists(checklist_path):
            raise Exception("Questionnaire not found. Please complete Phase 3 first.")

        # Initialize FounderSimulationAgent
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Initializing AI simulation..."
        )

        from src.agents.founder_simulation_agent import FounderSimulationAgent
        from src.models.founder_simulation_models import FounderSimulationConfig

        # Create config to use analysis reports instead of ref-data
        # Respect USE_MOCK_LLM environment variable
        use_mock_llm = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        use_real_llm = not use_mock_llm

        config = FounderSimulationConfig(
            company_dir=company_dir,
            simulation_type="reference_docs",
            use_real_llm=use_real_llm
        )

        agent = FounderSimulationAgent()

        # Update: Generating responses
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Generating AI responses from context..."
        )

        # Run simulation
        result = agent.process_simulation(company_dir, config)

        if not result.success:
            raise Exception(result.error_message or "Simulation processing failed")

        processing_time = time.time() - start_time

        # Build response
        qa_result = {
            "success": True,
            "qa_file": result.output_file,
            "processing_time": processing_time,
            "metadata": {
                "mode": "ai_simulation",
                **(result.metadata or {})
            }
        }

        # Update: Complete
        job_manager.update_status(
            job_id,
            JobStatus.COMPLETED,
            "Q&A simulation completed successfully!",
            result=qa_result
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error running Q&A simulation: {error_details}")

        job_manager.update_status(
            job_id,
            JobStatus.FAILED,
            f"Simulation failed: {str(e)}",
            error=str(e)
        )


def run_qa_upload_background(job_id: str, company_name: str, temp_file_path: str):
    """
    Background task for processing directly uploaded Q&A document.
    Extracts Q&A pairs and saves as founders-qa-responses.md.
    """
    start_time = time.time()

    try:
        # Update: Starting processing
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Processing uploaded Q&A document..."
        )

        # Sanitize company name
        sanitized_company_name = OutputManager.sanitize_company_name(company_name)
        company_dir = f"outputs/{sanitized_company_name}"

        # Verify company directory exists
        if not os.path.exists(company_dir):
            raise Exception(f"Company directory not found: {company_dir}")

        # Process with QADocProcessor
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Extracting Q&A pairs from document..."
        )

        from src.processors.qa_doc_processor import QADocProcessor

        processor = QADocProcessor()
        result = processor.process_qa_document(temp_file_path, company_dir)

        if not result.success:
            raise Exception(result.error_message or "Q&A processing failed")

        processing_time = time.time() - start_time

        # Build response
        qa_result = {
            "success": True,
            "qa_file": result.output_file,
            "processing_time": processing_time,
            "metadata": {
                "mode": "direct_upload",
                **(result.metadata or {})
            }
        }

        # Update: Complete
        job_manager.update_status(
            job_id,
            JobStatus.COMPLETED,
            "Q&A document processed successfully!",
            result=qa_result
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing Q&A upload: {error_details}")

        job_manager.update_status(
            job_id,
            JobStatus.FAILED,
            f"Upload processing failed: {str(e)}",
            error=str(e)
        )
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass


def run_memo_generation_background(job_id: str, company_name: str, agent_weights: dict):
    """
    Background task to generate final investment memo.
    Uses weighted analysis from selected agents and founder Q&A responses.
    """
    start_time = time.time()

    try:
        # Update: Starting memo generation
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Starting final memo generation..."
        )

        # Sanitize company name for directory consistency
        sanitized_company_name = OutputManager.sanitize_company_name(company_name)
        company_dir = f"outputs/{sanitized_company_name}"

        # Check prerequisites
        if not os.path.exists(company_dir):
            raise Exception(f"Company directory not found: {company_dir}")

        qa_responses_path = os.path.join(company_dir, "founders-qa-responses.md")
        if not os.path.exists(qa_responses_path):
            raise Exception("Founder Q&A responses not found. Please complete Phase 4 first.")

        # Initialize final memo processor
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Initializing memo processor..."
        )

        from src.processors.final_memo_processor import create_final_memo_processor

        processor = create_final_memo_processor()

        # Check prerequisites
        prerequisites_met, issues = processor.check_prerequisites(company_dir)
        if not prerequisites_met:
            raise Exception(f"Prerequisites not met: {'; '.join(issues)}")

        # Update: Generating memo
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Generating investment memo with weighted analysis..."
        )

        # Generate memo
        result = processor.generate_memo(company_dir, agent_weights)

        if not result.success:
            raise Exception(result.error_message or "Memo generation failed")

        processing_time = time.time() - start_time

        # Build response
        memo_result = {
            "success": True,
            "memo_file": result.output_file,
            "pdf_file": result.pdf_file,
            "processing_time": processing_time,
            "metadata": {
                "content_length": len(result.memo_content),
                "agent_weights_used": agent_weights,
                "generation_timestamp": result.timestamp.isoformat(),
                **(result.metadata or {})
            }
        }

        # Update: Complete
        job_manager.update_status(
            job_id,
            JobStatus.COMPLETED,
            "Final investment memo generated successfully!",
            result=memo_result
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating final memo: {error_details}")

        job_manager.update_status(
            job_id,
            JobStatus.FAILED,
            f"Memo generation failed: {str(e)}",
            error=str(e)
        )


@router.post("/simulate-qa", response_model=RunAnalysisResponse)
async def simulate_qa_responses(
    request: SimulateQARequest,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Simulate founder Q&A responses using AI based on questionnaire and company context.

    Requires Phase 3 (questionnaire generation) to be completed first.
    Uses questionnaire from Phase 3 and analysis reports as reference documents.
    """

    # Validate request
    if not request.company_name or not request.company_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Company name is required"
        )

    # Check if company directory exists
    sanitized_company_name = OutputManager.sanitize_company_name(request.company_name)
    company_dir = f"outputs/{sanitized_company_name}"

    if not os.path.exists(company_dir):
        raise HTTPException(
            status_code=400,
            detail=f"Company directory not found. Please complete Phase 1 first."
        )

    # Check if questionnaire exists (Phase 3 requirement)
    checklist_path = os.path.join(company_dir, "founders-checklist.md")
    if not os.path.exists(checklist_path):
        raise HTTPException(
            status_code=400,
            detail=f"Questionnaire not found. Please complete Phase 3 (multi-agent analysis) first."
        )

    # Create job
    job_id = job_manager.create_job()

    # Start background simulation
    background_tasks.add_task(
        run_simulation_background,
        job_id,
        request.company_name
    )

    return RunAnalysisResponse(
        job_id=job_id,
        message="Q&A simulation started.",
        company_name=request.company_name,
        selected_agents=[]
    )


@router.post("/upload-qa", response_model=RunAnalysisResponse)
async def upload_qa_document(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload pre-answered Q&A document (MD, PDF, DOCX).

    Processes and saves as founders-qa-responses.md.
    """

    # Validate company name
    if not company_name or not company_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Company name is required"
        )

    # Validate file format
    allowed_extensions = [".md", ".pdf", ".docx", ".txt"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(allowed_extensions)}"
        )

    # Check company directory exists
    sanitized_company_name = OutputManager.sanitize_company_name(company_name)
    company_dir = f"outputs/{sanitized_company_name}"

    if not os.path.exists(company_dir):
        raise HTTPException(
            status_code=400,
            detail=f"Company directory not found. Please complete Phase 1 first."
        )

    # Save uploaded file temporarily
    temp_dir = "outputs/temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, f"{sanitized_company_name}_qa_upload{file_ext}")

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Create job
    job_id = job_manager.create_job()

    # Start background processing
    background_tasks.add_task(
        run_qa_upload_background,
        job_id,
        company_name,
        temp_file_path
    )

    return RunAnalysisResponse(
        job_id=job_id,
        message="Q&A document upload started. Processing...",
        company_name=company_name,
        selected_agents=[]
    )


@router.post("/generate-memo", response_model=GenerateMemoResponse)
async def generate_final_memo(
    request: GenerateMemoRequest,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Generate final investment memo with weighted analysis.

    Requires:
    - Phase 3 (multi-agent analysis) completed
    - Phase 4 (founder Q&A simulation or upload) completed

    The memo will synthesize findings based on the provided agent weights.
    """

    # Validate request
    if not request.company_name or not request.company_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Company name is required"
        )

    if not request.agent_weights:
        raise HTTPException(
            status_code=400,
            detail="Agent weights are required"
        )

    # Check company directory exists
    sanitized_company_name = OutputManager.sanitize_company_name(request.company_name)
    company_dir = f"outputs/{sanitized_company_name}"

    if not os.path.exists(company_dir):
        raise HTTPException(
            status_code=400,
            detail=f"Company directory not found. Please complete Phase 1 first."
        )

    # Check Phase 4 prerequisite (Q&A responses)
    qa_responses_path = os.path.join(company_dir, "founders-qa-responses.md")
    if not os.path.exists(qa_responses_path):
        raise HTTPException(
            status_code=400,
            detail=f"Founder Q&A responses not found. Please complete Phase 4 (Q&A simulation or upload) first."
        )

    # Check analysis directory exists (Phase 3 prerequisite)
    analysis_dir = os.path.join(company_dir, "analysis")
    if not os.path.exists(analysis_dir):
        raise HTTPException(
            status_code=400,
            detail=f"Analysis directory not found. Please complete Phase 3 (multi-agent analysis) first."
        )

    # Create job
    job_id = job_manager.create_job()

    # Start background memo generation
    background_tasks.add_task(
        run_memo_generation_background,
        job_id,
        request.company_name,
        request.agent_weights
    )

    return GenerateMemoResponse(
        job_id=job_id,
        message="Final memo generation started.",
        company_name=request.company_name
    )
