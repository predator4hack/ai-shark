import yaml
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PromptManager:
    _instance = None
    _prompts = None
    _version = None
    _yaml_file_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PromptManager, cls).__new__(cls)
            cls._instance._load_prompts()
        return cls._instance

    def _load_prompts(self):
        """Loads prompts from the YAML file."""
        if not self._yaml_file_path.exists():
            logger.error(f"Prompt file not found at {self._yaml_file_path}")
            raise FileNotFoundError(f"Prompt file not found at {self._yaml_file_path}")

        try:
            with open(self._yaml_file_path, 'r') as f:
                data = yaml.safe_load(f)
            self._version = data.get("version", "unknown")
            self._prompts = data.get("prompts", {})
            logger.info(f"Prompts loaded successfully from {self._yaml_file_path}, version: {self._version}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing prompts.yaml: {e}")
            raise ValueError(f"Error parsing prompts.yaml: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading prompts: {e}")
            raise RuntimeError(f"An unexpected error occurred while loading prompts: {e}")

    def get_prompt_template(self, prompt_key: str, version: Optional[str] = None) -> str:
        """
        Retrieves a prompt template by its key and optional version.

        Args:
            prompt_key: The base key of the prompt to retrieve (e.g., "slide_analysis").
            version: Optional. The version of the prompt to retrieve (e.g., "v1", "v2").
                     If not provided, or if the versioned prompt is not found, it falls back
                     to the base prompt_key.

        Returns:
            The prompt template string.

        Raises:
            ValueError: If the prompt key (or its versioned variant) is not found.
        """
        if version:
            versioned_key = f"{prompt_key}_{version}"
            template = self._prompts.get(versioned_key, {}).get("template")
            if template:
                return template
            else:
                logger.warning(f"Versioned prompt '{versioned_key}' not found. Falling back to base prompt '{prompt_key}'.")

        template = self._prompts.get(prompt_key, {}).get("template")
        if template is None:
            logger.error(f"Prompt template '{prompt_key}' (and any requested version) not found in {self._yaml_file_path}")
            raise ValueError(f"Prompt template '{prompt_key}' not found.")
        return template

    def format_prompt(self, prompt_key: str, version: Optional[str] = None, **kwargs) -> str:
        """
        Retrieves and formats a prompt template with the given parameters.

        Args:
            prompt_key: The base key of the prompt to retrieve.
            version: Optional. The version of the prompt to retrieve.
            **kwargs: Parameters to format the prompt template with.

        Returns:
            The formatted prompt string.

        Raises:
            ValueError: If the prompt key (or its versioned variant) is not found.
            KeyError: If a required parameter for formatting is missing.
        """
        template = self.get_prompt_template(prompt_key, version)
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing parameter for prompt '{prompt_key}' (version: {version or 'default'}): {e}")
            raise KeyError(f"Missing parameter for prompt '{prompt_key}' (version: {version or 'default'}): {e}")

    @property
    def version(self) -> str:
        """Returns the version of the prompts file."""
        return self._version