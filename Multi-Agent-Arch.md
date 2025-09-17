# Final MVP Architecture - Startup Clarification Engine

## System Overview

LangChain-based orchestrated workflow that processes markdown files from a directory to generate investor questionnaires. The system uses specialized agents to analyze different aspects of startup data and identifies gaps before synthesizing questions.

## Architecture Components

### 1. Document Loader & Parser

**Purpose**: Load and prepare input data for processing
**Input**: Directory containing `pitch_deck.md` and `public_data.md`
**Output**: Structured document objects for agent processing

**Implementation Details**:

-   Use `pathlib` to read files from specified directory
-   Parse markdown using `python-markdown` or `mistune`
-   Create LangChain Document objects with metadata
-   Chunk large documents if needed for LLM context limits
-   Validate file existence and handle missing files gracefully

### 2. LangChain Orchestrator Agent

**Purpose**: Main coordinator that manages the entire analysis workflow
**Input**: Parsed document objects
**Output**: Coordinates all specialist agents and manages execution flow

**Implementation Details**:

-   Initialize LangChain AgentExecutor with custom tools
-   Maintain conversation memory across agent interactions
-   Define execution sequence: Analysis Agents → Gap Analyzer → Question Synthesis
-   Handle error recovery and partial failures
-   Manage LLM context and token limits across agent calls
-   Use LangChain's `ConversationBufferMemory` for maintaining context

### 3. Business Analysis Agent

**Purpose**: Analyze business model, revenue streams, and scalability
**Input**: Full startup data context
**Output**: Business insights and preliminary questions

**Analysis Focus**:

-   Revenue stream identification and classification
-   Business model sustainability and scalability
-   Customer acquisition strategy and cost structure
-   Competitive positioning and differentiation
-   Market entry and expansion strategies

**LangChain Implementation**:

-   Custom tool with specific business analysis prompts
-   Return structured analysis with identified gaps
-   Use chain-of-thought prompting for comprehensive analysis

### 4. Financial Analysis Agent

**Purpose**: Analyze financial projections, metrics, and funding requirements
**Input**: Full startup data context
**Output**: Financial insights and preliminary questions

**Analysis Focus**:

-   Revenue and expense projections validation
-   Key financial metrics and unit economics
-   Funding requirements and use of funds
-   Burn rate, runway, and cash flow analysis
-   Valuation assumptions and benchmarking

**LangChain Implementation**:

-   Custom tool with financial analysis capabilities
-   Structured output format for consistent processing
-   Integration with LangChain's math tools if calculations needed

### 5. Market & Competition Agent

**Purpose**: Analyze market opportunity, competition, and positioning
**Input**: Full startup data context
**Output**: Market insights and preliminary questions

**Analysis Focus**:

-   Market size, growth, and segmentation
-   Competitive landscape and differentiation
-   Market timing and entry barriers
-   Customer validation and product-market fit
-   Go-to-market strategy evaluation

**LangChain Implementation**:

-   Market research focused prompts and analysis
-   Competitor identification and comparison frameworks
-   Output structured market assessment data

### 6. Technology & Product Agent

**Purpose**: Analyze technical feasibility, product roadmap, and IP
**Input**: Full startup data context
**Output**: Technology insights and preliminary questions

**Analysis Focus**:

-   Technology stack evaluation and scalability
-   Product development roadmap and milestones
-   Intellectual property and technical moats
-   Technical team capabilities and requirements
-   Platform architecture and security considerations

**LangChain Implementation**:

-   Technical analysis prompts with engineering focus
-   Product roadmap evaluation frameworks
-   Technical risk assessment capabilities

### 7. Risk Analysis Agent

**Purpose**: Identify and analyze various business risks
**Input**: Full startup data context
**Output**: Risk assessment and preliminary questions

**Analysis Focus**:

-   Business model and execution risks
-   Market and competitive risks
-   Technology and operational risks
-   Financial and regulatory risks
-   Team and leadership risks

**LangChain Implementation**:

-   Risk identification and categorization prompts
-   Risk impact and probability assessment
-   Mitigation strategy evaluation

### 8. Gap Analyzer Agent

**Purpose**: Identify information gaps and missing critical data across all analyses
**Input**: Outputs from all analysis agents + original startup data
**Output**: Comprehensive gap analysis and priority areas for questioning

**Core Functions**:

-   **Cross-Agent Analysis**: Compare insights from all agents to identify contradictions or missing connections
-   **Completeness Check**: Verify essential investor information is available (financials, market size, team, etc.)
-   **Inconsistency Detection**: Flag conflicting information between pitch deck and public data
-   **Critical Gap Identification**: Prioritize gaps that significantly impact investment decisions
-   **Context-Aware Analysis**: Consider industry-specific requirements and standards

**Implementation Details**:

-   Receive structured outputs from all analysis agents
-   Use comparison prompts to identify missing information
-   Generate gap report with categories: Critical, Important, Minor
-   Include specific references to source documents for context
-   Output structured gap analysis for question generation

### 9. Question Synthesis Agent

**Purpose**: Generate final investor questionnaire based on gap analysis and agent insights
**Input**: Gap analysis report + all agent outputs
**Output**: Structured markdown questionnaire

**Core Functions**:

-   **Question Generation**: Create specific, actionable questions for each identified gap
-   **Categorization**: Group questions by domain (Business, Financial, Market, Tech, Risk)
-   **Deduplication**: Remove redundant or overlapping questions
-   **Context Linking**: Reference specific pitch deck sections or data points
-   **Formatting**: Structure output as clean markdown with proper categorization

**Question Categories**:

```markdown
# Investor Clarification Questions

## Business Model & Revenue

-   [Questions about revenue streams, scalability, etc.]

## Financial Analysis

-   [Questions about projections, metrics, funding]

## Market & Competition

-   [Questions about market size, competition, positioning]

## Technology & Product

-   [Questions about tech stack, roadmap, IP]

## Risk Assessment

-   [Questions about identified risks and mitigation]
```

## Data Flow Architecture

```
Input Directory → Document Loader → Orchestrator Agent
                                        ↓
                     Business Agent ← → Financial Agent
                           ↓               ↓
                     Market Agent ← → Technology Agent
                           ↓               ↓
                     Risk Agent → Gap Analyzer Agent
                                        ↓
                              Question Synthesis Agent
                                        ↓
                              questionnaire.md Output
```

## Implementation Stack

### Core Dependencies

```python
langchain>=0.1.0
langchain-openai  # or langchain-anthropic
python-markdown>=3.5
pathlib  # built-in
tiktoken  # for token counting
pydantic>=2.0  # for data models
```

### Key LangChain Components

-   `AgentExecutor`: Main orchestration
-   `ConversationBufferMemory`: Context management
-   `StructuredOutputParser`: Consistent agent outputs
-   `PromptTemplate`: Specialized prompts for each agent
-   Custom tools for each analysis agent

### File Structure

```
/project
  /input_data
    pitch_deck.md
    public_data.md
  /src
    orchestrator.py
    agents/
      business_agent.py
      financial_agent.py
      market_agent.py
      technology_agent.py
      risk_agent.py
      gap_analyzer.py
      question_synthesis.py
  output/
    questionnaire.md
```

## Error Handling & Validation

### Input Validation

-   Check file existence and readability
-   Validate markdown format and content structure
-   Handle empty or corrupted files

### Agent Execution

-   Timeout handling for long-running LLM calls
-   Partial failure recovery (continue with available analysis)
-   Token limit management and context truncation
-   Rate limiting for API calls

### Output Validation

-   Ensure questionnaire completeness
-   Validate markdown formatting
-   Check question quality and relevance

## Execution Flow

1. **Initialize**: Load documents and create agent instances
2. **Analysis Phase**: Run all analysis agents in parallel or sequence
3. **Gap Analysis**: Process all agent outputs to identify information gaps
4. **Question Generation**: Synthesize targeted questions based on gaps
5. **Output**: Write structured questionnaire to markdown file

This architecture provides a complete, implementable system for analyzing startup data and generating investor questionnaires using LangChain's agent framework.
