import argparse
import os
import glob

from unstructured.partition.auto import partition

from src.agents.evaluation_agent import EvaluationAgent


def find_latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)


def main():
    parser = argparse.ArgumentParser(description="Evaluate generated questions against a founder checklist.")
    parser.add_argument("--company-name", required=True, help="The name of the company.")
    args = parser.parse_args()

    company_name_lower = args.company_name.lower()

    # Find the generated questions file
    generated_questions_pattern = f"outputs/{company_name_lower}-founders-checklist.md"
    generated_questions_file = find_latest_file(generated_questions_pattern)
    if not generated_questions_file:
        print(f"Error: Could not find generated questions file for {args.company_name}.")
        return

    # Find the founder checklist file
    founder_checklist_pattern = f"assets/Company Data/*/LV -*Checklist*.pdf"
    founder_checklist_files = glob.glob(founder_checklist_pattern, recursive=True)
    founder_checklist_file = None
    for f in founder_checklist_files:
        if company_name_lower in f.lower():
            founder_checklist_file = f
            break

    if not founder_checklist_file:
        # try docx
        founder_checklist_pattern = f"assets/Company Data/*/LV -*Checklist*.docx"
        founder_checklist_files = glob.glob(founder_checklist_pattern, recursive=True)
        for f in founder_checklist_files:
            if company_name_lower in f.lower():
                founder_checklist_file = f
                break

    if not founder_checklist_file:
        print(f"Error: Could not find founder checklist file for {args.company_name}.")
        return

    print(f"Found generated questions file: {generated_questions_file}")
    print(f"Found founder checklist file: {founder_checklist_file}")

    # Read the content of the files
    with open(generated_questions_file, "r") as f:
        generated_questions = f.read()

    elements = partition(founder_checklist_file)
    founder_checklist = "\n".join([str(el) for el in elements])

    # Instantiate the evaluation agent
    agent = EvaluationAgent()

    # Analyze the questions
    evaluation_result = agent.analyze(
        founder_checklist=founder_checklist,
        generated_questions=generated_questions,
    )

    # Print the result
    print("\n--- Evaluation Result ---")
    print(evaluation_result.summary)
    for criterion in evaluation_result.criteria:
        print(f"- {criterion.criterion}: {criterion.score}/10")
        print(f"  Justification: {criterion.justification}")
    if evaluation_result.suggestions:
        print("\nSuggestions for improvement:")
        for suggestion in evaluation_result.suggestions:
            print(f"- {suggestion}")


if __name__ == "__main__":
    main()
