# Final Memo Agent

**Objective**: Come up with final investment memo based on the /outputs/<company-name>/ans-founders-checklist.md and all the agent analysis in /outputs/<company-name>/analysis/ based on the agent weights provided by the user

## Implementation Plan

1. Analyse the streamlit_app.py and understand the workflow. Once the ans-founders-checklist.md is created either by simulating founders answers or by user directly uploading the Q&A document, the UI should show one input box corresponding to each agent. The user should enter the values out of 100 and the sum of values of all the agents should be 100 as well

example

```
Agent A: __/100
Agnet B: __/100
Agent C: __/100
```

There should be proper checks as the sum of values for all agents should not exceed 100 in UI before submitting. You can auto fill for the last agent or something. So basically do every checks and make sure that the values are appropriate and only then these values are passed for processing.

2. Once you have the values, you have to pass these values with corresponsding agnet name and agent analysis from previous steps to the LLM.

The prompt parameter for passing the values and agent analysis content could look like:

```
{
    "agents": [
        {
            "agent_name": "Business Analysis Agent",
            "weight": 30,
            "analysis": "..."
        },
        {
            "agent_name": "Market Analysis Agent",
            "weight": 70,
            "analysis": "..."
        },
    ]
}
```

Another parameter that should be passed to the LLM prompt is the ans-founders-checklist.md. Write a prompt asking LLM to come up with a final investment memo based on the agent analysis and percentage of weightage it should give to that particular analysis. So for example, user has provided 60 to founder analysis agent, then the recommendation and investment memo should have 60% wieghtage to founder analysis.

3. The final investment memo should be stored in the /outputs/<company-name>/investment-memo.md. In addition to that, in the UI, the user should get option to download the pdf version of it.

Please reuse code as much as possible. If you have a task, look for it in the project if it already has been implemented. Analyse the whole project and you will be able to reuse components

Clarifying Questions

1. Agent Discovery: Should I dynamically discover available agents from
   the /outputs/<company>/analysis/ directory (like business_analysis.md,
   market_analysis.md) or should I hardcode a list of expected agents?
   Dynamically discover agents, you can find an implementation already in the code to discover the agents

2. UI Placement: Where exactly should the Final Memo Agent section
   appear? Should it be:

-   A new section after the founder simulation section?
-   Integrated into the existing display_results() function?
-   A separate tab/page?

A new section after the founder simulation section

3. Weight Input Validation: For the weight validation (must sum to
   100), should I:

-   Auto-fill the last agent to make it sum to 100?
-   Show real-time validation errors?
-   Allow submission only when sum equals 100?

4. Agent Names: Should I use the agent file names (e.g.,
   "business_analysis") or create user-friendly display names (e.g.,
   "Business Analysis Agent")?
   Use agent file names without underscore, replace with whitespace

5. LLM Integration: Should I create a new agent class (like
   FinalMemoAgent) or integrate directly into the streamlit app? What LLM
   service should I use (same as other agents)?
   create a MemoAgent class, use LLM service same as other agents

6. Output Format: Any specific format requirements for the final
   investment memo beyond saving it as
   /outputs/<company>/final-investment-memo.md?
   Save a pdf copy as well, the user should also get the option to download the pdf version

7. Error Handling: What should happen if:

-   No analysis files exist? Pass to the agent mentioning no analysis found for the startup.
-   No ans-founders-checklist.md exists? Throw error saying file does not exist
-   Some agent analysis files are missing? Mention for the specific agent that "No data available" when you are creating the json object in the analysis field

---

## Comprehensive Implementation Plan

Based on the analysis of the project structure and existing implementations, here's a detailed plan for implementing the Final Memo Agent feature:

### 1. Architecture Overview

The implementation will follow the existing project patterns:

- **Agent Pattern**: Create `FinalMemoAgent` following `BaseAnalysisAgent` structure
- **Model Pattern**: Create Pydantic models for data validation
- **Processor Pattern**: Create utility classes for file handling and processing
- **UI Pattern**: Add new section to Streamlit app after founder simulation

### 2. Files to Create/Modify

#### New Files:
1. `src/agents/final_memo_agent.py` - Main agent class
2. `src/models/final_memo_models.py` - Pydantic models for data structures
3. `src/processors/final_memo_processor.py` - Business logic and file handling
4. `src/utils/pdf_generator.py` - PDF generation utility (if not exists)

#### Modified Files:
1. `src/ui/streamlit_app.py` - Add new UI section
2. `src/processors/analysis_pipeline.py` - Integration point (if needed)

### 3. Implementation Details

#### 3.1 Data Models (`src/models/final_memo_models.py`)

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional

class AgentWeight(BaseModel):
    agent_name: str
    weight: int = Field(..., ge=0, le=100)
    analysis: str
    
class FinalMemoRequest(BaseModel):
    agents: List[AgentWeight]
    founders_checklist_content: str
    company_name: str
    
    @field_validator('agents')
    @classmethod
    def validate_weights_sum_100(cls, v):
        total = sum(agent.weight for agent in v)
        if total != 100:
            raise ValueError(f"Weights must sum to 100, got {total}")
        return v

class FinalMemoResult(BaseModel):
    success: bool
    memo_content: str
    output_file: str
    pdf_file: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: float
    metadata: Optional[Dict] = None
```

#### 3.2 Agent Implementation (`src/agents/final_memo_agent.py`)

```python
class FinalMemoAgent(BaseAnalysisAgent):
    """Agent for generating final investment memos"""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None, **kwargs):
        super().__init__(
            agent_name="FinalMemoAgent",
            llm=llm,
            **kwargs
        )
        
    def generate_final_memo(self, request: FinalMemoRequest) -> FinalMemoResult:
        """Generate final investment memo based on weighted agent analysis"""
        # Implementation here
        
    def get_system_prompt(self) -> str:
        """Return system prompt for final memo generation"""
        
    def get_analysis_prompt_template(self) -> PromptTemplate:
        """Return prompt template for final memo"""
```

#### 3.3 Processor Implementation (`src/processors/final_memo_processor.py`)

```python
class FinalMemoProcessor:
    """Handles final memo generation business logic"""
    
    def __init__(self):
        self.agent = FinalMemoAgent()
        
    def discover_analysis_files(self, company_dir: str) -> List[str]:
        """Dynamically discover analysis files in the analysis directory"""
        
    def load_analysis_content(self, analysis_dir: str) -> Dict[str, str]:
        """Load content from all analysis files"""
        
    def generate_memo(self, company_dir: str, agent_weights: Dict[str, int]) -> FinalMemoResult:
        """Main method to generate final memo"""
        
    def save_memo_as_pdf(self, markdown_content: str, output_path: str) -> str:
        """Convert markdown memo to PDF"""
```

#### 3.4 Streamlit UI Integration

Add new section in `streamlit_app.py`:

```python
def final_memo_section():
    """Final investment memo generation section"""
    # Check prerequisites (ans-founders-checklist.md exists)
    # Discover available analysis files
    # Create weight input controls
    # Validate weights sum to 100
    # Generate memo button
    # Display results with download options

def display_final_memo_results():
    """Display final memo results with download options"""
    # Show memo preview
    # Provide markdown download
    # Provide PDF download
```

### 4. Implementation Sequence

#### Phase 1: Core Infrastructure
1. Create data models with validation
2. Create FinalMemoAgent with basic LLM integration
3. Create FinalMemoProcessor with file discovery logic

#### Phase 2: Business Logic
1. Implement analysis file discovery (reuse from AnalysisPipeline)
2. Implement content loading and parsing
3. Create LLM prompt for final memo generation
4. Implement memo generation logic

#### Phase 3: UI Integration
1. Add final_memo_section() to streamlit_app.py
2. Implement weight input validation with real-time feedback
3. Add memo generation and display functionality
4. Integrate PDF generation and download

#### Phase 4: PDF Generation
1. Create or enhance PDF generation utility
2. Integrate with memo generation workflow
3. Add download functionality to UI

### 5. Key Reusable Components

From existing codebase:
- `AnalysisPipeline.discover_available_agents()` - Agent discovery pattern
- `BaseAnalysisAgent` - Agent architecture pattern
- `LLMManager` - LLM integration
- `OutputManager` - File management utilities
- Existing Pydantic models - Validation patterns
- Session state management from streamlit_app.py

### 6. Error Handling Strategy

1. **Missing Analysis Files**: Graceful degradation with "No data available" messages
2. **Missing Founders Checklist**: Clear error message with instructions
3. **Weight Validation**: Real-time UI feedback preventing invalid submissions
4. **LLM Failures**: Retry logic and fallback error messages
5. **PDF Generation Failures**: Fallback to markdown-only with clear messaging

### 7. User Experience Flow

1. User completes founder simulation (prerequisite)
2. System automatically discovers available analysis agents
3. UI presents weight input controls for each discovered agent
4. Real-time validation ensures weights sum to 100
5. User clicks "Generate Final Memo" button
6. System processes request and generates memo
7. User can preview memo and download in markdown/PDF formats

### 8. Integration Points

- **Post-Founder Simulation**: Trigger final memo section visibility
- **Analysis Pipeline**: Reuse agent discovery logic
- **Session State**: Store memo results for download access
- **File Management**: Follow existing output directory patterns

### 9. Testing Strategy

1. Unit tests for data models and validation
2. Integration tests for agent and processor logic
3. UI tests for weight validation and user interactions
4. End-to-end tests with sample company data

This implementation plan ensures consistency with existing patterns while delivering the required functionality with proper error handling and user experience considerations.
