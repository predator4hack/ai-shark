## Task: Questionnaire Agent

**Objective:** Generate structured questions by the investor to the founders clarifying the gaps from various reports provided. This questinnaire document should contain all the question that isn't present or cross-question the fesability or other aspects or need more information from the founders to make a sound investment descision.

**Implementation Details**

1. Analyse the questionnaire_agent.py file, questionnaire pipeline associated with it.
2. Instead of taking investment memo(/results/analysis_results.md), the questionnaire agent should intake all the reports from various analysis agents, Business Analysis Agent(/outputs/<company-name>-business-analysis.md), Market Analysis Agent(/outputs/<company-name>-market-analysis.md) etc(more agent reports to come)
3. Based on the reports ingested, the agent should understand the business and clarify all the questions an investor would ask to the founding team to make a sound investment descision.
4. The output should be saved as /outputs/<company-name>-founders-checklist.md.

You may need to modify the existing pipeline and prompt in questionnaire_agent.py file

Sample Questions:

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

More about implementation:

1. Company Name Extraction: How should I extract the company name for the
   output filename? Take input from user, this should be the input variable of the module
2. Report Discovery: Should the agent:

    - Look for specific naming patterns (e.g., <company-name>-\*.md)?

3. New Prompt Template: Should I create a new prompt template version
   (e.g., questionaire_agent_v4) specifically for this multi-report analysis,
   or modify the existing v3 template?
   Create a new prompt

## Detailed Implementation Plan

### Overview
Transform the existing questionnaire_agent.py from a single investment memo analyzer to a multi-report analysis system that generates founder-focused questionnaires based on business analysis, market analysis, and other agent reports.

### Implementation Steps

#### Step 1: Update Function Signatures and Parameters
**File:** `questionnaire_agent.py`
**Changes:**
1. Modify `generate_questions_with_retry()` function signature:
   - Remove `investment_memo: str` parameter
   - Add `company_name: str` parameter
   - Add `reports_dir: str = "outputs"` parameter (optional, defaults to "outputs")

2. Update main execution block:
   - Remove hardcoded file reading from `results/analysis_results.md`
   - Add command-line argument parsing or user input for company name
   - Example: `python questionnaire_agent.py --company-name "sia"`

#### Step 2: Implement Multi-Report Discovery and Loading
**File:** `questionnaire_agent.py`
**New Function:** `load_analysis_reports(company_name: str, reports_dir: str) -> dict`
**Logic:**
1. Scan the `reports_dir` directory for files matching pattern: `{company_name}-*.md`
2. Read content from matching files
3. Return dictionary with report types as keys and content as values
   ```python
   {
       "business_analysis": "content of sia-business-analysis.md",
       "market_analysis": "content of sia-market-analysis.md",
       # ... other reports
   }
   ```
4. Handle file not found gracefully with informative error messages
5. Log which reports were found and loaded

#### Step 3: Create New Prompt Template
**File:** `config/prompts.yaml`
**New Template:** `questionaire_agent_v4`
**Template Structure:**
1. **Role Definition:** Senior VC analyst conducting founder due diligence
2. **Context:** Multiple analysis reports instead of single investment memo
3. **Input Format:** Template should accept multiple report contents:
   ```yaml
   template: |
     **Role:** You are a principal-level investment analyst...
     
     **Analysis Reports:**
     {% if business_analysis %}
     **Business Analysis Report:**
     ---
     {{business_analysis}}
     ---
     {% endif %}
     
     {% if market_analysis %}
     **Market Analysis Report:**
     ---
     {{market_analysis}}
     ---
     {% endif %}
     
     # Additional report sections as needed
   ```
4. **Question Categories:** Focus on founder-specific questions aligned with sample questions in spec:
   - Revenue Streams & Business Model
   - Unit Economics & Financials (CAC, LTV, MRR, ARR, Burn, Runway)
   - Pricing Strategy & Scalability
   - Technology Stack & Infrastructure
   - Founder Profiles & Team Composition
   - Fundraising & Valuation Strategy
   - Operational Processes & Facilities
   - Risk Assessment & Mitigation Plans

#### Step 4: Update Prompt Manager Integration
**File:** `questionnaire_agent.py`
**Function:** `generate_questions_with_retry()`
**Changes:**
1. Update prompt manager call:
   ```python
   prompt = prompt_manager.format_prompt(
       "questionaire_agent",
       version="v4",
       **reports_dict  # Unpack the reports dictionary
   )
   ```
2. Pass individual report contents as named parameters to the prompt template

#### Step 5: Update Output File Handling
**File:** `questionnaire_agent.py`
**Changes:**
1. Replace UUID-based filename with company-specific naming:
   ```python
   output_file = f"outputs/{company_name}-founders-checklist.md"
   ```
2. Ensure the `outputs` directory exists, create if needed
3. Add proper error handling for file writing operations
4. Include metadata in output file (generation timestamp, reports analyzed)

#### Step 6: Error Handling and Validation
**Enhancements:**
1. **Input Validation:**
   - Validate company name parameter (non-empty, valid filename characters)
   - Check if reports directory exists
   - Validate at least one analysis report is found

2. **Graceful Degradation:**
   - If some reports are missing, proceed with available reports
   - Log warnings for missing expected reports
   - Include note in output about which reports were analyzed

3. **Error Messages:**
   - Clear error messages for missing company name
   - Informative messages when no reports found
   - API failure handling with retry mechanism (already exists)

#### Step 7: Update Main Execution Flow
**File:** `questionnaire_agent.py`
**New Main Block:**
```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate founder questionnaire from analysis reports')
    parser.add_argument('--company-name', required=True, help='Company name for report discovery')
    parser.add_argument('--reports-dir', default='outputs', help='Directory containing analysis reports')
    
    args = parser.parse_args()
    
    try:
        # Load analysis reports
        reports = load_analysis_reports(args.company_name, args.reports_dir)
        
        # Generate questionnaire
        questions = generate_questions_with_retry(args.company_name, reports)
        
        # Save output
        output_file = f"{args.reports_dir}/{args.company_name}-founders-checklist.md"
        with open(output_file, "w") as f:
            f.write(questions)
        
        print(f"Founder questionnaire saved to: {output_file}")
        
    except Exception as e:
        print(f"Error generating questionnaire: {e}")
```

#### Step 8: Testing Strategy
**Test Cases:**
1. **Successful Multi-Report Analysis:**
   - Company: "sia"
   - Reports: sia-business-analysis.md, sia-market-analysis.md
   - Expected: founders-checklist.md generated successfully

2. **Partial Reports Available:**
   - Only business analysis available
   - Should proceed with available data

3. **No Reports Found:**
   - Invalid company name
   - Should provide clear error message

4. **Invalid Input Handling:**
   - Empty company name
   - Non-existent reports directory

### File Structure After Implementation
```
/Users/chandankumar/myspace/ai-shark/
├── questionnaire_agent.py (modified)
├── config/prompts.yaml (updated with v4 template)
├── outputs/
│   ├── sia-business-analysis.md (input)
│   ├── sia-market-analysis.md (input)
│   └── sia-founders-checklist.md (output)
```

### Backward Compatibility
- Keep existing prompt templates (v1, v2, v3) intact
- Maintain existing function structure where possible
- Add new functionality without breaking existing workflows

### Dependencies
- No new external dependencies required
- Uses existing: google.generativeai, dotenv, PromptManager
- May add argparse for command-line interface (built-in Python module)

### Success Criteria
1. ✅ Company name accepted as input parameter
2. ✅ Multiple analysis reports automatically discovered and loaded
3. ✅ New prompt template processes multiple reports effectively
4. ✅ Output saved as `{company-name}-founders-checklist.md` in outputs directory
5. ✅ Generated questions focus on founder-specific inquiries as per sample
6. ✅ Error handling for missing reports and invalid inputs
7. ✅ Maintains existing API retry and error handling mechanisms
