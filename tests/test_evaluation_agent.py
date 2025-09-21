"""
Test and Demonstration Script for EvaluationAgent

This script serves a dual purpose:
1. It validates the functionality of the EvaluationAgent and its strategies.
2. It provides a standalone, runnable example of how to use the agent to evaluate
   a set of generated questions, both with and without a founder checklist.

To run this script:
    python -m tests.test_evaluation_agent
"""

import os
import json
from typing import Optional

# Ensure the script can find the src module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.evaluation_agent import create_evaluation_agent
from src.models.evaluation_models import EvaluationResult

# --- Sample Data ---

GENERATED_QUESTIONS = """
**Team:**
1. What specific prior experience does the founding team have in the logistics and supply chain industry?
2. Are there any key roles (e.g., CTO, Head of Sales) that are currently vacant?

**Market Opportunity:**
1. The market size is projected to be $5B. What is the bottom-up analysis to support this?
2. Who are the primary competitors, and what is the company's unique, sustainable advantage?

**Financials:**
1. The financial model projects 300% year-over-year growth. What are the core assumptions driving this?
"""

FOUNDER_CHECKLIST = """
**1. Team Background:**
   - Founder experience in the industry.
   - Key management roles and expertise.
   - Advisory board strength.

**2. Market and Competition:**
   - Total Addressable Market (TAM) validation.
   - Competitive landscape and differentiation.
   - Go-to-market strategy.

**3. Financial Projections:**
   - Revenue model and assumptions.
   - Key metrics (CAC, LTV).
   - Funding requirements and use of funds.
"""

# --- Test Runner ---

def run_evaluation(
    generated_questions: str,
    founder_checklist_content: Optional[str] = None,
    checklist_path: Optional[str] = "temp_checklist.txt",
) -> Optional[EvaluationResult]:
    """
    A helper function to set up the environment, run the evaluation,
    and clean up temporary files.
    """
    agent = None
    result = None

    try:
        # Create a temporary checklist file if content is provided
        if founder_checklist_content and checklist_path:
            with open(checklist_path, "w") as f:
                f.write(founder_checklist_content)
            # Use the path to the created file
            agent = create_evaluation_agent(founder_checklist_path=checklist_path)
        else:
            # Run without a checklist file
            agent = create_evaluation_agent(founder_checklist_path=None)

        print(f"\n--- Running Evaluation with {agent.strategy.__class__.__name__} ---")

        # Perform the analysis
        result = agent.analyze(
            generated_questions=generated_questions,
            founder_checklist=founder_checklist_content,
        )

    except Exception as e:
        print(f"An error occurred during evaluation: {e}")
        # Re-raise for test frameworks that need to catch it
        raise
    finally:
        # Clean up the temporary file
        if checklist_path and os.path.exists(checklist_path):
            os.remove(checklist_path)

    return result

def print_result(title: str, result: Optional[EvaluationResult]):
    """
    Prints the evaluation result in a formatted way.
    """
    print(f"\n--- {title} ---")
    if not result:
        print("Evaluation did not produce a result.")
        return

    print(f"\n[Summary]: {result.summary}")
    if result.notes:
        print(f"[Notes]: {result.notes}")

    print("\n[Evaluation Criteria]:")
    for criterion in result.criteria:
        print(f"  - {criterion.criterion}: {criterion.score}/10")
        print(f"    Justification: {criterion.justification}")

    if result.suggestions:
        print("\n[Suggestions for Improvement]:")
        for suggestion in result.suggestions:
            print(f"  - {suggestion}")
    print("\n" + "="*50)


if __name__ == "__main__":
    """
    Main execution block to run the two demonstration scenarios.
    """
    # --- Scenario 1: Evaluation WITH a Founder Checklist ---
    print("SCENARIO 1: Running evaluation with a founder checklist.")
    result_with_checklist = run_evaluation(
        generated_questions=GENERATED_QUESTIONS,
        founder_checklist_content=FOUNDER_CHECKLIST,
    )
    print_result("Result with Checklist", result_with_checklist)

    # Basic validation for the test
    assert result_with_checklist is not None
    assert len(result_with_checklist.criteria) > 0
    print("\n✅ Scenario 1 completed successfully.")

    # --- Scenario 2: Evaluation WITHOUT a Founder Checklist (Expert Mode) ---
    print("\nSCENARIO 2: Running evaluation without a founder checklist.")
    result_without_checklist = run_evaluation(generated_questions=GENERATED_QUESTIONS)
    print_result("Result without Checklist (Expert Mode)", result_without_checklist)

    # Basic validation for the test
    assert result_without_checklist is not None
    assert len(result_without_checklist.criteria) > 0
    assert result_without_checklist.notes is not None # Expect a note about missing checklist
    print("\n✅ Scenario 2 completed successfully.")

    print("\nAll scenarios executed.")
