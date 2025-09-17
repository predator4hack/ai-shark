# Market & Competition Agent

**Purpose**: Analyze market opportunity, competition, and positioning
**Input**: Startup's data from Pitch Deck(/results/analysis_results.md) and scrapped publically available data(/results/public_data.md)
**Output**: Market insights about the sector, competitors and company.

**Analysis Focus**:

-   Market size, growth, and segmentation
-   Competitive landscape and differentiation
-   Market timing and entry barriers
-   Customer validation and product-market fit
-   Go-to-market strategy evaluation
-   Mention the GAPS that you find, be it data unavaiailability for proper analysis or red flags in the market data. Basically you can mention anything that you'd want clarifications from the startup founder to make investment descisions as a market analyst

## Implementation Details

1. Analyse the demo_analysis_pipeline.py which implements a business analyst agent, extend it with market analysis agent.
2. Provide option to execute the type of agent to run when executing demo_analysis_pipeline.py
3. Process:
    - Load the documents Pitch Deck(/results/analysis_results.md) and scrapped publically available data(/results/public_data.md), there might already be an implementation of that, see if you can re-use that code.
    - Analyse both the documents using LLM mentioning which one is Public and Pitch Deck data
    - Generate Markdown Reports - save the results in markdown format as '/outputs/<company-name>-market-analysis.md'
    - Display summary

Keep in mind the design principles and structure the code so that code is reusable.

1. Agent Type Selection Logic

The spec mentions "Provide option to execute the type of agent to run when
executing demo_analysis_pipeline.py" - How exactly should this option be
provided?

-   Interactive menu during execution

2. Market Analysis Model Usage

I see there's already a MarketAnalysis model in
src/models/analysis_models.py with comprehensive fields like:

-   market_size, competition, positioning, market_trends, etc.

Should the new Market & Competition Agent:

-   Check the code in demo_analysis_pipeline.py and see how it's done with Business analysis agent. I believe you may not need a data model, just get the content in markdown format.

3. Output Format Clarification

The spec mentions "Generate Markdown Reports" but the existing business
agent has both:

-   Markdown analysis output, as in the business analyst agent in demo_analysis_pipeline.py. Consider that as source of truth and main file in the project. Also, you can change the logic to name of the file from combined_business_analysis.md to '/outputs/<company-name>-business-analysis.md' in case you want to reuse the existing code for saving the results.

For the market agent, which approach should I follow:

-   Only markdown output like the current business agent's combined analysis?
-   Yes, like current business agent, in markdown format

4. File Naming Convention

The spec says save results as '/outputs/<company-name>-market-analysis.md' -
How should the company name be determined?

-   Extract from document content automatically from pitch deck data, keep a default name as well

5. Agent Integration Architecture

Looking at the current structure, should the Market Agent:

-   Inherit from BaseStructuredAgent like the business agent?
-   Be a completely separate agent class?
-   Be integrated as an additional method within the existing
    BusinessAnalysisAgent?
-   Follow the same pattern with a create_market_agent() factory function?

Answer: This I let you decide, I would want you to implement whatever would be best design pattern for this purpose, keep in mind that there will be more agents that may be integrated in future.

6. Input Document Processing

The spec mentions analyzing "Pitch Deck(/results/analysis_results.md) and
scrapped publicly available data(/results/public_data.md)" - Should the
market agent:

-   Use the same document loading logic as the business agent

7. Competitive Analysis Depth

Given the focus on "competition and positioning," what level of detail is
expected:

-   Basic competitor identification and positioning? - YES
-   Deep competitive feature comparison? - YES
-   Market share analysis? - YES
-   Pricing strategy analysis? - YES
-   Should it attempt to identify competitors not mentioned in the documents? - NO, ALWAYS rely on the data you have been provided only for analysis

    With the given data, do Whatever analysis you can perform.

8. Pipeline Integration

How should this integrate with the existing pipeline:

-   Replace the current business analysis?
-   Run alongside business analysis?
-   Run as a separate pipeline option?
-   Combine results from both agents into one report?

I want option to run the type of analyst. with respect to the design pattern, you can follow whichever suits best for the project.

---

## Detailed Implementation Steps

### Phase 1: MarketAnalysisAgent Creation
1. **Create `src/agents/market_agent.py`**
   - Follow the same pattern as `BusinessAnalysisAgent` in `src/agents/business_agent.py`
   - Inherit from `BaseStructuredAgent` or `BaseAnalysisAgent` depending on the chosen approach
   - Implement core methods:
     - `get_system_prompt()`: Define market analysis system prompt focusing on competition, market size, positioning
     - `get_analysis_prompt_template()`: Create LangChain PromptTemplate for market analysis
     - `analyze_combined_documents()`: Main analysis method similar to business agent's implementation
   - Include specialized market analysis logic for:
     - Market size, growth, and segmentation analysis
     - Competitive landscape mapping and differentiation analysis
     - Market timing and entry barriers assessment
     - Customer validation and product-market fit evaluation
     - Go-to-market strategy assessment
     - Gap identification and red flag detection

2. **Create factory function `create_market_agent()`**
   - Similar to `create_business_agent()` in business_agent.py
   - Handle LLM initialization and configuration
   - Return configured MarketAnalysisAgent instance

### Phase 2: Document Processing and Company Name Extraction

1. **Implement company name extraction utility**
   - Create function to parse pitch deck content for company name
   - Look for patterns like "Company Name:", title sections, or document headers
   - Implement fallback logic (e.g., "startup-analysis" if no name found)
   - Add to `src/utils/` directory or integrate into existing utilities

2. **Enhance LLM prompt for company name and sector identification**
   - **Instruct LLM to include company name as a heading** in the analysis output for easier extraction
   - **Require LLM to identify and prominently mention the company's sector/industry** early in the analysis
   - Format requirement: "# [Company Name] - Market & Competition Analysis" as the main heading
   - Sector identification requirement: Clearly state the industry/sector in the executive summary
   - This ensures reliable extraction and sector-specific analysis context

3. **Implement sector-specific analysis logic**
   - **Tailor market analysis based on identified sector** (e.g., fintech, healthcare, SaaS, e-commerce)
   - Include sector-specific considerations:
     - **Regulatory landscape** relevant to the sector
     - **Industry-specific metrics** and KPIs
     - **Sector competition patterns** and market dynamics
     - **Technology trends** affecting the specific industry
     - **Customer behavior** patterns typical for the sector
   - Create sector-specific prompt templates or dynamic prompt adjustment based on identified industry

4. **Enhance document processing**
   - Reuse existing document loading logic from `demo_analysis_pipeline.py`
   - Ensure clear identification of Pitch Deck vs Public Data sources
   - Maintain existing document structure and metadata
   - Add sector detection preprocessing to inform analysis approach

### Phase 3: Pipeline Integration and Agent Selection
1. **Modify `demo_analysis_pipeline.py`**
   - Add interactive agent selection menu:
     ```
     Select Analysis Type:
     1. Business Analysis
     2. Market & Competition Analysis
     3. Both (run sequentially)
     ```
   - Implement agent selection logic in `main()` function
   - Create new methods:
     - `run_market_analysis_pipeline()`: Market-specific pipeline
     - `run_combined_pipeline()`: Both agents sequentially
     - `get_agent_selection()`: Interactive menu handler

2. **Update existing methods**
   - Modify `run_pipeline()` to `run_business_pipeline()` for clarity
   - Update file naming logic to support dynamic company names
   - Change from `combined_business_analysis.md` to `<company-name>-business-analysis.md`

### Phase 4: Market Analysis Implementation

1. **Design sector-aware market analysis prompt**
   - Focus on the 6 key analysis areas mentioned in requirements
   - **Emphasize sector-specific analysis approach**:
     - Include sector identification as a mandatory first step
     - Tailor competitive analysis based on industry dynamics
     - Apply sector-relevant regulatory considerations
     - Use industry-appropriate metrics and benchmarks
   - Emphasize gap identification and red flag detection with sector context
   - Include specific instructions for data source attribution (Pitch Deck vs Public Data)
   - **Mandatory output format**: Start with "# [Company Name] - Market & Competition Analysis"
   - **Required sector statement**: Include "**Industry/Sector**: [Identified Sector]" in executive summary
   - Structure output for comprehensive markdown report generation with sector-specific insights

2. **Implement analysis methods**
   - `analyze_market_documents()`: Core market analysis logic with sector awareness
   - `_identify_company_sector()`: Sector identification from document content
   - `_get_sector_specific_prompt()`: Dynamic prompt adjustment based on identified sector
   - `generate_market_markdown_report()`: Report generation with proper naming and sector context
   - `_extract_company_name()`: Enhanced company name extraction from LLM-generated headings
   - `_display_market_pipeline_summary()`: Summary display logic including sector information

### Phase 5: Report Generation and File Management

1. **Implement sector-aware market report generation**
   - Create markdown report structure focusing on:
     - **Executive Summary** (with mandatory company name heading and sector identification)
     - **Industry/Sector Analysis** (sector-specific context and dynamics)
     - **Market Size & Growth Analysis** (sector-relevant metrics and benchmarks)
     - **Competitive Landscape** (industry-specific competition patterns)
     - **Market Positioning & Differentiation** (sector context for positioning)
     - **Go-to-Market Strategy Assessment** (industry-appropriate strategies)
     - **Regulatory & Compliance Considerations** (sector-specific requirements)
     - **Technology & Industry Trends** (sector-relevant technological developments)
     - **Identified Gaps & Red Flags** (sector-informed risk assessment)
     - **Investment Decision Considerations** (industry-specific investment criteria)
   - Use template similar to business analysis but market-focused with sector specialization
   - Include metadata: processing time, document sources, analysis date, identified sector

2. **File naming and organization**
   - Implement dynamic file naming: `<company-name>-market-analysis.md`
   - Create summary file: `<company-name>-market-summary.md`
   - Ensure files are saved in `/outputs/` directory
   - Handle edge cases (invalid characters in company names, etc.)

### Phase 6: Error Handling and Validation
1. **Add comprehensive error handling**
   - Document loading failures
   - LLM API errors and retries
   - Invalid company name extraction
   - Missing required document sections

2. **Implement validation**
   - Verify required documents exist (analysis_results.md, public_data.md)
   - Validate LLM responses for completeness
   - Check output file generation success

### Phase 7: Testing and Integration
1. **Create test cases**
   - Unit tests for MarketAnalysisAgent
   - Integration tests for pipeline flow
   - Test company name extraction with various document formats
   - Test error scenarios and edge cases

2. **Update existing imports and dependencies**
   - Add market agent imports to `__init__.py` files
   - Update demo_analysis_pipeline.py imports
   - Ensure all dependencies are properly configured

### Phase 8: Documentation and Code Quality
1. **Add comprehensive documentation**
   - Docstrings for all new methods and classes
   - Type hints throughout the codebase
   - Update README or docs if needed

2. **Code quality assurance**
   - Follow existing code style and patterns
   - Ensure proper logging throughout
   - Maintain consistency with existing agent architecture

### Design Decisions Made:

1. **Architecture**: Separate MarketAnalysisAgent class following the same pattern as BusinessAnalysisAgent
2. **Integration**: Pipeline modification with interactive menu selection
3. **Output**: Markdown-only format following business agent pattern
4. **Reusability**: Modular design allowing easy addition of future agents
5. **File Management**: Dynamic naming based on extracted company names
6. **Error Handling**: Comprehensive validation and fallback mechanisms
7. **Sector-Specific Analysis**: LLM-driven sector identification and tailored analysis approach
8. **Enhanced Extraction**: LLM-generated standardized headings for reliable company name extraction
9. **Industry Context**: Sector-aware competitive analysis, regulatory considerations, and market dynamics

### Files to be Created/Modified:
- **New**: `src/agents/market_agent.py`
- **Modified**: `demo_analysis_pipeline.py`
- **Modified**: `src/agents/__init__.py` (if needed for imports)
- **New/Modified**: Company name extraction utility
- **Updated**: Test files for new functionality

This implementation plan ensures a robust, extensible solution that maintains consistency with existing codebase patterns while providing the flexibility to add more agents in the future.
