# Analysis Pipeline Integration

**Objective**: Analyse the demo_analysis_pipeline.py and streamlit_app.py and understand these pipeline. Integrate the existing demo analysis pipeline into the streamlit app data processing pipeline.

## Implementation Details

1. Analyse the streamlit_app.py application and understand the pitch deck and additional data processing pipeline. Currently, the user uploads the pitch deck and additional documents(Optional) and they are being processed and the output is stored in the /outputs/<company-name>/ directory.

Once the processing is done, there should be a UI button to initiate the analysis pipeline which would use the processed pitch_deck.md, additional data(look for files in /outputs/<company-name>/additional_docs/), and public_data.md stored in /outpus/<company-name>/

1. Analyse the demo_analysis_pipeline.py and understand how the pipeline is working. The module currently accepts inputs from user about:
    - Weather to use LLM or use mock response
    - Which analysis agents to use

While integrating the analysis pipeline, it should always use LLMs and use all the agents available to do the analysis.

After the analysis, the outputs of agent analyzers should be stored in /outputs/<company-name>/analysis/

Try to reuse the demo_analysis_pipeline.py(Currently supports only pitch_deck.md and public_data.md, need to add analysis for any additional data provided as well), rename it and put it inside appropriate directory. Don't forget to fix the import statements once you move it to a different directory.

Clarifying Questions:

1. Additional Data Handling: I notice the current
   demo_analysis_pipeline.py only handles pitch_deck.md and
   public_data.md. How should I handle additional documents that might be
   in /outputs/<company-name>/additional_docs/? Should they be
   concatenated, analyzed separately, or combined with the main analysis?

Yes, you can concatenate all the additional documents into one .md file, store in /outputs/<company-name>/additional_docs/ and then pass the concatenated data to the LLM in addition to pitch_deck.md, public_data.md

2.  Agent Selection: The spec says to "use all agents available" -
    should I run both BusinessAnalysisAgent AND MarketAnalysisAgent and
    combine their outputs, or run them in sequence?
    No need to combine the outputs, outputs of each agent should be stored in separate files in /outputs/<company-name>/analysis/. For now, run all the agents sequentially.
3.  Output Organization: Should the analysis results be stored in
    /outputs/<company-name>/analysis/ with separate files for each agent
    (e.g., business_analysis.md, market_analysis.md) or combined into a
    single comprehensive report?
    Keep separate files

4.  UI Integration: After the analysis is complete, should the
    Streamlit app display the analysis results inline, or just provide
    links/paths to the generated files?
    No output in UI as of now, there will be another pipeline that needs to work on the outputs of these anlysis agents and we need to provide results of that in UI

5.  Public Data Source: I see the analysis pipeline expects
    public_data.md but in the streamlit output structure, this file may or
    may not exist. How should I handle cases where no public data was
    collected?
    In that case, you can pass empty string to the LLM

6.  Processing Flow: Should the analysis button only appear after both
    pitch deck and additional documents are processed, or can it work with
    just the pitch deck?
    It can just work with Pitch Deck

## Detailed Implementation Plan

### Phase 1: Setup and Directory Structure
1. **Create Analysis Pipeline Module**
   - Create `src/processors/` directory if not exists
   - Move `demo_analysis_pipeline.py` to `src/processors/analysis_pipeline.py`
   - Update all import statements to reflect new location

2. **Update Import Dependencies**
   - Fix relative imports in moved file
   - Ensure compatibility with existing project structure
   - Test imports to verify no breaking changes

### Phase 2: Enhance Analysis Pipeline Core
1. **Modify AnalysisPipelineDemo Class**
   - Rename class to `AnalysisPipeline` (remove Demo suffix)
   - Remove interactive user input functionality (agent selection, LLM choice)
   - Hard-code to use real LLM and all available agents
   - Modify constructor to accept company directory path instead of results directory

2. **Update Document Loading Logic**
   - Modify `load_documents()` method to work with company-specific directory structure
   - Load from `/outputs/<company-name>/pitch_deck.md`
   - Load from `/outputs/<company-name>/public_data.md` (handle if missing)
   - Load and concatenate all files from `/outputs/<company-name>/additional_docs/` if directory exists

3. **Implement Additional Documents Handling**
   - Create new method `load_additional_documents()` to scan additional_docs directory
   - Concatenate all additional documents into single content string
   - Store concatenated content as virtual document for analysis

### Phase 3: Multi-Agent Analysis Implementation
1. **Create Agent Discovery System**
   - Implement `discover_available_agents()` method to dynamically find all analysis agents
   - Scan `src.agents` module for classes inheriting from `BaseAnalysisAgent`
   - Use reflection to get agent factory functions (e.g., `create_business_agent`, `create_market_agent`)
   - Create agent registry that maps agent names to their factory functions

2. **Implement Dynamic Multi-Agent Execution**
   - Create new method `run_all_agents_analysis()` that works with any number of agents
   - Dynamically instantiate all discovered agents using their factory functions
   - Run analysis for each agent with all three document types (pitch_deck, public_data, additional_docs)
   - Return dictionary with results from each agent, keyed by agent name/type

3. **Update Output Generation for Scalability**
   - Modify `generate_combined_markdown_report()` to handle variable number of agents
   - Create separate output files for each agent in `/outputs/<company-name>/analysis/`
   - Use agent names to generate filenames (e.g., `business_analysis.md`, `market_analysis.md`, `<new_agent>_analysis.md`)
   - Create dynamic analysis summary file with overview of all executed agent results

### Phase 4: Streamlit UI Integration
1. **Add Analysis Section to Streamlit App**
   - Add new section in `streamlit_app.py` after document processing sections
   - Create `analysis_section()` function
   - Add "🧠 Run Analysis" button that appears when pitch deck is processed

2. **Implement Analysis Trigger**
   - Create `run_analysis()` function in streamlit app
   - Check for required files (at minimum pitch_deck.md)
   - Initialize and execute AnalysisPipeline
   - Update session state with analysis results
   - Show progress indicators during analysis

3. **Analysis Status Display**
   - Add analysis results section to `display_results()`
   - Show analysis completion status
   - Display paths to generated analysis files
   - Handle error cases gracefully

### Phase 5: Error Handling and Validation
1. **Input Validation**
   - Verify company directory exists
   - Check for minimum required files (pitch_deck.md)
   - Handle missing public_data.md gracefully
   - Validate additional_docs directory access

2. **Error Handling**
   - Implement comprehensive try-catch blocks
   - Provide meaningful error messages in UI
   - Log errors for debugging
   - Graceful degradation when some documents are missing

3. **Progress Tracking**
   - Add progress bars for analysis operations
   - Show current agent being executed
   - Display time estimates
   - Handle timeouts appropriately

### Phase 6: File Structure and Organization
1. **Output Directory Management**
   - Ensure `/outputs/<company-name>/analysis/` directory creation
   - Implement proper file naming conventions
   - Handle file overwriting scenarios
   - Add timestamps to analysis files

2. **Content Processing**
   - Implement additional document concatenation logic
   - Add metadata to concatenated files
   - Ensure proper markdown formatting
   - Handle various file formats in additional_docs

### Phase 7: Integration Testing
1. **Unit Testing**
   - Test AnalysisPipeline class independently
   - Verify document loading functions
   - Test multi-agent execution
   - Validate output file generation

2. **Integration Testing**
   - Test full workflow from Streamlit UI
   - Verify with different document combinations
   - Test error scenarios
   - Validate file paths and outputs

3. **End-to-End Testing**
   - Complete workflow testing with real documents
   - Performance testing with large documents
   - Memory usage validation
   - UI responsiveness testing

### Implementation Details

#### Key Files to Modify/Create:
1. `src/processors/analysis_pipeline.py` (moved and modified from demo_analysis_pipeline.py)
2. `src/ui/streamlit_app.py` (add analysis section and integration)
3. Update any import references to the moved pipeline

#### New Methods Required:
- `AnalysisPipeline.__init__(company_dir, use_real_llm=True)`
- `AnalysisPipeline.discover_available_agents()`
- `AnalysisPipeline.load_additional_documents()`
- `AnalysisPipeline.run_all_agents_analysis()`
- `AnalysisPipeline.generate_agent_specific_reports()`
- `streamlit_app.analysis_section()`
- `streamlit_app.run_analysis()`

#### Directory Structure After Implementation:
```
/outputs/<company-name>/
├── pitch_deck.md
├── public_data.md (optional)
├── metadata.json
├── table_of_contents.json
├── additional_docs/ (optional)
│   ├── document1.md
│   ├── document2.md
│   └── ...
└── analysis/
    ├── business_analysis.md
    ├── market_analysis.md
    ├── <additional_agent>_analysis.md  # Dynamically generated for each agent
    └── analysis_summary.md
```

#### Success Criteria:
1. Analysis pipeline can be triggered from Streamlit UI
2. **All available agents are discovered and run automatically** using real LLM
3. **System scales to handle new agents without code changes** (just add agent file and factory function)
4. Analysis works with minimum requirement (pitch_deck.md only)
5. Additional documents are properly incorporated when available
6. **Separate analysis files are generated dynamically for each discovered agent**
7. Error handling provides clear feedback to users
8. Performance is acceptable for typical document sizes
9. **Agent discovery system works with future agents** that follow the established patterns

This plan provides a comprehensive roadmap for any developer to implement the analysis pipeline integration while maintaining code quality and user experience.
