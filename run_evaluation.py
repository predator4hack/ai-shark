"""
Standalone Script to Run the Evaluation Agent

This script runs the EvaluationAgent on the output of the QuestionnaireAgent.
File paths are configured directly in the `if __name__ == '__main__':` block.

Usage:
    1. Configure the `COMPANY_DIR_TO_EVALUATE` and `GROUND_TRUTH_CHECKLIST_PATH` variables below.
    2. Run the script from your terminal: `python run_evaluation.py`
"""

import os
import sys
from typing import Optional

# Attempt to import docx and PyPDF2 for handling different file types
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not found. DOCX ground truth checklists will not be supported.")

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not found. PDF ground truth checklists will not be supported.")

from src.agents.evaluation_agent import create_evaluation_agent
from src.models.evaluation_models import EvaluationResult


def _extract_text_from_docx(file_path: str) -> str:
    """
    Extracts plain text from a .docx file.
    """
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx is not installed. Cannot process .docx files.")
    
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


def _extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts plain text from a .pdf file.
    """
    if not PDF_AVAILABLE:
        raise ImportError("PyPDF2 is not installed. Cannot process .pdf files.")
    
    reader = PdfReader(file_path)
    full_text = []
    for page in reader.pages:
        full_text.append(page.extract_text())
    return '\n'.join(full_text)


def print_result(title: str, result: Optional[EvaluationResult]):
    """
    Prints the evaluation result in a user-friendly formatted way.
    """
    print(f"\n--- {title} ---")
    if not result:
        print("Evaluation failed to produce a result.")
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
    print("\n" + "=" * 70)


def main(company_dir: str, ground_truth_checklist: Optional[str] = None, questionnaire_file: str = "founders-checklist.md"):
    """
    Main function to run the evaluation pipeline with direct file path inputs.

    Args:
        company_dir: Path to the company's output directory (e.g., 'outputs/cashvisory').
        ground_truth_checklist: (Optional) Path to the ground-truth checklist file.
        questionnaire_file: Filename of the generated questionnaire to evaluate.
    """
    # --- 1. Validate Paths ---
    if not os.path.isdir(company_dir):
        print(f"Error: Company directory not found at '{company_dir}'")
        sys.exit(1)

    questionnaire_path = os.path.join(company_dir, questionnaire_file)
    if not os.path.isfile(questionnaire_path):
        print(f"Error: Generated questionnaire not found at '{questionnaire_path}'")
        sys.exit(1)

    if ground_truth_checklist and not os.path.isfile(ground_truth_checklist):
        print(f"Error: Ground truth checklist not found at '{ground_truth_checklist}'")
        sys.exit(1)

    # --- 2. Read Input Files ---
    print(f"Reading generated questionnaire from: {questionnaire_path}")
    with open(questionnaire_path, 'r', encoding='utf-8') as f:
        generated_questions = f.read()

    founder_checklist_content = None
    if ground_truth_checklist:
        print(f"Reading ground truth checklist from: {ground_truth_checklist}")
        file_extension = os.path.splitext(ground_truth_checklist)[1].lower()

        try:
            if file_extension == '.docx':
                founder_checklist_content = _extract_text_from_docx(ground_truth_checklist)
            elif file_extension == '.pdf':
                founder_checklist_content = _extract_text_from_pdf(ground_truth_checklist)
            elif file_extension in ['.md', '.txt']:
                with open(ground_truth_checklist, 'r', encoding='utf-8') as f:
                    founder_checklist_content = f.read()
            else:
                print(f"Warning: Unsupported ground truth checklist file type: {file_extension}. Attempting to read as plain text.")
                with open(ground_truth_checklist, 'r', encoding='utf-8') as f:
                    founder_checklist_content = f.read()
        except ImportError as ie:
            print(f"Error: {ie}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading ground truth checklist '{ground_truth_checklist}': {e}")
            sys.exit(1)

    # --- 3. Run Evaluation ---
    try:
        # The factory function will automatically select the correct strategy
        agent = create_evaluation_agent(founder_checklist_path=ground_truth_checklist)

        print(f"\nRunning evaluation with {agent.strategy.__class__.__name__}...")

        result = agent.analyze(
            generated_questions=generated_questions,
            founder_checklist=founder_checklist_content
        )

        # --- 4. Display Results ---
        title = f"Evaluation Result for {os.path.basename(company_dir)}"
        print_result(title, result)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # --- CONFIGURE YOUR INPUTS HERE ---

    # 1. Set the path to the company's output directory you want to evaluate.
    COMPANY_DIR_TO_EVALUATE = "outputs/cashvisory"

    # 2. (Optional) Set the path to a ground-truth checklist file.
    #    If set to None, the agent will run in "Expert Mode".
    #    Supported formats: .md, .txt, .docx, .pdf
    GROUND_TRUTH_CHECKLIST_PATH = "outputs/cashvisory/ref-data/ref-founders-checklist.md" # Example: "assets/Company Data/01. Data stride/01. LV - Founders Checklist - Datastride Analytics.pdf"

    # --- RUN THE SCRIPT ---
    print("Starting evaluation script...")
    main(
        company_dir=COMPANY_DIR_TO_EVALUATE,
        ground_truth_checklist=GROUND_TRUTH_CHECKLIST_PATH
    )
    print("\nEvaluation script finished.")
