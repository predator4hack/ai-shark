## Task: Questionnaire Agent

**Objective:** Generate structured questions by the investor to the founders clarifying the gaps from various reports provided. This questinnaire document should contain all the question that isn't present or cross-question the fesability or other aspects or need more information from the founders to make a sound investment descision.

**Implementation Details**

1. Analyse the questionnaire_agent.py file, questionnaire pipeline associated with it. Also, analyse the analysis_pipeline.py and understand the flow. Once all the agents are executed and analysis are stored, the questionnaire agent should run automatically.
2. Instead of taking investment memo(/results/analysis_results.md), the questionnaire agent should intake all the reports from various analysis agents stored in /outputs/<company-name>/analysis/
3. Based on the reports ingested, the agent should understand the business and clarify all the questions an investor would ask to the founding team to make a sound investment descision.
4. The output should be saved as /outputs/<company-name>/founders-checklist.md.
5. There should be a download button in UI so that the founders-checklist file can be downloaded in docx format.

You may need to modify the existing pipeline and prompt in questionnaire_agent.py file.

Also I am planning to remove the questionnaire_agent.py file so don't keep any dependency on it. Create new python modules and put it in appropriate directory.

Sample Questions that can be in founder-checklit(not exhaustive list):

```
Revenue Streams
    ● Clearly define all sources of revenue. For each stream, include:
        ○ Name of the Revenue Stream: (e.g., Subscription Fees, Commission, Product Sales).
    ○ Description:
        ■ What is it?
        ■ How does it work?
    ○ Target Audience: Who is paying?
    ○ Percentage Contribution: Share of total revenue (if available).

Pricing Strategy – Separate sheet attached
    ● Rationale behind pricing – Straight feature pricing, considering our costs and margins, future expansion costs, enterprise ROIs, existing competitors pricing, and discounts

Unit Economics:
    - Customer Acquision Cost (CAC)
    - Lifetime Value (LTV)
    - LTV

Recurring vs. One-Time Revenue
Segregate revenue into:
    - Recurring Revenue
    - One-Time Revenue

Payment Flow and Terms
    - How payments are collected and processed.

Scalability of Revenue Model

Competitor Analysis Framework
(cover 2-3 competitors operating in the similar revenue model or advanced revenue model in
comparison to your company)


Founders Profile of all the founders

Financials:
    - MRR
    - ARR
    - Burn
    - Runway
    - Gross Margin

Facilities:


Technology:
● Write up on Tech stack –

Fundraiser:

Valuation:

Round structure:

Following the above information, we request you to provide a detailed business note for reference
in the format below:
● Key Problems Solved –
● Business Model –

Pipeline:

Why now?:

Financials:

Risk And Mitigation:
```

Clarification Questions:

1. Integration Trigger: Should the questionnaire agent be:

-   A separate module that the pipeline calls after generating reports?

2. Module Structure: Where should I place the new questionnaire
   functionality?

-   src/agents/questionnaire_agent.py (following the agent pattern)?
-   src/processors/questionnaire_processor.py (following the processor
    pattern)?

I am actually not sure here. So basically the questionnaire agent is collecting the information from all the previous agents and come up with questions that will be outputed. What pattern do you think should it follow?

3. Prompt Management:

-   Keep using the existing PromptManager with "questionaire_agent" v4
    prompt

4. Error Handling: How should the system behave if:

-   No analysis reports are found in the /analysis/ directory?
-   Some analysis reports are corrupted or empty?

    Assume that the reports won't be empty and there will be at least one report. If there is not report or everything is currpoted, log error and stop the processing

-   The LLM fails to generate the questionnaire? NO Output

5. Company Directory Structure: Should the questionnaire respect the new
   structure where we have:

-   /outputs/<company-name>/analysis/ for agent reports
-   /outputs/<company-name>/founders-checklist.md for the questionnaire

Respect the new structure

---

## Implementation Plan

### Architecture Decision

Based on the requirements analysis, the questionnaire functionality should follow the **processor pattern** rather than agent pattern because:

-   It's a **post-processing step** that aggregates and synthesizes outputs from multiple agents
-   It doesn't perform independent analysis but rather **collects and questions** existing analysis
-   It fits the data processing pipeline workflow better than the analysis agent workflow

### File Structure

```
src/
├── processors/
│   ├── questionnaire_processor.py    # Main questionnaire processor
│   └── docx_converter.py            # DOCX conversion utility
├── utils/
│   └── analysis_loader.py           # Utility to load analysis reports
└── models/
    └── questionnaire_models.py      # Data models for questionnaire
```

### Implementation Components

#### 1. Core Processor (`src/processors/questionnaire_processor.py`)

**Purpose**: Main questionnaire generation logic
**Key Functions**:

-   `QuestionnaireProcessor.__init__(company_dir, use_real_llm)`
-   `QuestionnaireProcessor.load_analysis_reports()` - Load from `/analysis/` directory
-   `QuestionnaireProcessor.generate_questionnaire()` - Call LLM with combined reports
-   `QuestionnaireProcessor.save_questionnaire()` - Save as markdown
-   `QuestionnaireProcessor.run()` - Main execution method

**Dependencies**:

-   PromptManager (existing) with "questionaire_agent" v4 prompt
-   LLM setup (existing Google Gemini configuration)
-   Analysis loader utility

#### 2. Analysis Loader Utility (`src/utils/analysis_loader.py`)

**Purpose**: Centralized logic for loading analysis reports
**Key Functions**:

-   `load_analysis_reports(company_dir)` - Load all `.md` files from `/analysis/`
-   `validate_reports(reports)` - Ensure reports are valid and non-empty
-   `format_reports_for_llm(reports)` - Format reports for LLM prompt

**Input**: `/outputs/<company-name>/analysis/*.md`
**Output**: Dictionary with report contents keyed by analysis type

#### 3. DOCX Converter (`src/processors/docx_converter.py`)

**Purpose**: Convert markdown questionnaire to DOCX format
**Key Functions**:

-   `convert_markdown_to_docx(markdown_path, docx_path)` - Main conversion
-   `format_questionnaire_docx(doc, content)` - Apply formatting and styling

**Dependencies**: `python-docx` library for document generation

#### 4. Data Models (`src/models/questionnaire_models.py`)

**Purpose**: Type definitions and data structures
**Classes**:

-   `QuestionnaireConfig` - Configuration for questionnaire generation
-   `AnalysisReport` - Structure for individual analysis reports
-   `QuestionnaireResult` - Result structure with metadata

#### 5. Integration Point (Modify `src/processors/analysis_pipeline.py`)

**Location**: `AnalysisPipeline.run_pipeline()` method around line 757
**Change**: Add questionnaire generation as final step after `generate_agent_specific_reports()`

```python
# After line 756: self.generate_agent_specific_reports(all_results)
# Add:
try:
    from ..processors.questionnaire_processor import QuestionnaireProcessor
    questionnaire_processor = QuestionnaireProcessor(self.company_dir, self.use_real_llm)
    questionnaire_result = questionnaire_processor.run()
    print(f"✅ Questionnaire generated: {questionnaire_result['output_file']}")
except Exception as e:
    print(f"⚠️ Questionnaire generation failed: {e}")
```

### Implementation Steps

#### Step 1: Create Analysis Loader Utility

-   [ ] Implement `src/utils/analysis_loader.py`
-   [ ] Handle file discovery from `/analysis/` directory
-   [ ] Implement report validation and error handling
-   [ ] Format reports for LLM consumption

#### Step 2: Create Data Models

-   [ ] Implement `src/models/questionnaire_models.py`
-   [ ] Define data structures for configuration and results
-   [ ] Add type hints and validation

#### Step 3: Implement Core Questionnaire Processor

-   [ ] Create `src/processors/questionnaire_processor.py`
-   [ ] Implement LLM integration using existing prompt
-   [ ] Add retry mechanism (copy from existing questionnaire_agent.py)
-   [ ] Implement markdown output generation

#### Step 4: Implement DOCX Converter

-   [ ] Create `src/processors/docx_converter.py`
-   [ ] Add `python-docx` dependency to requirements
-   [ ] Implement markdown to DOCX conversion
-   [ ] Add proper formatting and styling

#### Step 5: Integration with Analysis Pipeline

-   [ ] Modify `AnalysisPipeline.run_pipeline()` method
-   [ ] Add questionnaire generation as final step
-   [ ] Handle errors gracefully without breaking main pipeline

#### Step 6: UI Integration (Backend Support)

-   [ ] Ensure questionnaire files are accessible via API
-   [ ] Create endpoint to serve DOCX files for download
-   [ ] Add metadata about questionnaire generation status

### Error Handling Strategy

#### Report Loading Errors

-   **No reports found**: Log error and stop processing
-   **Corrupted reports**: Log error and stop processing
-   **Empty analysis directory**: Log error and stop processing

#### LLM Generation Errors

-   **API failure**: Use retry mechanism with exponential backoff
-   **Empty response**: Log error, no output file generated
-   **Malformed response**: Log error, no output file generated

#### File System Errors

-   **Permission issues**: Log error and fail gracefully
-   **Disk space**: Log error and fail gracefully
-   **Path issues**: Validate paths before processing

### Output Format

#### Markdown Output (`/outputs/<company-name>/founders-checklist.md`)

```markdown
# Founder Questionnaire for {Company Name}

**Generated:** {timestamp}
**Reports Analyzed:** {list of analysis types}
**Total Reports:** {count}

---

{LLM-generated questionnaire content}
```

#### DOCX Output (`/outputs/<company-name>/founders-checklist.docx`)

-   Professionally formatted document
-   Table of contents
-   Structured sections matching markdown
-   Proper heading hierarchy
-   Company branding placeholders

### Integration Testing

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test with analysis pipeline
3. **End-to-End Tests**: Test complete flow with sample data
4. **Error Case Tests**: Test all error scenarios

### Dependencies

-   **Existing**: PromptManager, LLM setup, file utilities
-   **New**: `python-docx` for DOCX generation
-   **Modified**: `analysis_pipeline.py` for integration

### Backward Compatibility

-   Remove `questionnaire_agent.py` after implementation
-   Ensure no other modules depend on old questionnaire agent
-   Update any references in documentation or scripts

### Future Extensibility

-   **Custom prompts**: Allow different questionnaire styles
-   **Multiple formats**: Support PDF, Word templates
-   **Dynamic questions**: Based on industry or company stage
-   **Question prioritization**: Mark critical vs. optional questions
