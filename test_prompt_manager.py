from src.utils.prompt_manager import PromptManager
prompt_manager = PromptManager()

# prompt = prompt_manager.format_prompt(
#     prompt_key="topic_analysis",
#     topic="Problem",
#     version="v2"
# )

prompt = prompt_manager.format_prompt(
    prompt_key="topic_extraction"
)

print(prompt)