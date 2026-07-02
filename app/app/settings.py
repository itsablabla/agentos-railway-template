"""
App Settings
============

Shared runtime objects for the platform.
"""

from os import getenv
from agno.models.openai import OpenAI, OpenAIResponses


def default_model() -> OpenAI | OpenAIResponses:
    """Fresh model instance per agent — avoids shared-state footguns.
    
    Uses custom LLM if CUSTOM_LLM_API_KEY and CUSTOM_LLM_BASE_URL are set,
    otherwise falls back to OpenAI.
    """
    custom_api_key = getenv("CUSTOM_LLM_API_KEY")
    custom_base_url = getenv("CUSTOM_LLM_BASE_URL")
    custom_model_id = getenv("CUSTOM_LLM_MODEL_ID", "custom-model")
    
    if custom_api_key and custom_base_url:
        return OpenAI(
            id=custom_model_id,
            api_key=custom_api_key,
            base_url=custom_base_url,
        )
    
    return OpenAIResponses(id="gpt-5.4")

