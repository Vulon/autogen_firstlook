from autogen_core.models import ChatCompletionClient
from autogen_firstlook.settings import Settings
from autogen_ext.models.ollama import OllamaChatCompletionClient


def create_model_client(settings: Settings) -> ChatCompletionClient:
    if settings.client_type == "ollama":
        return OllamaChatCompletionClient(model=settings.llm_model)
    raise ValueError(f"Unsupported client type: {settings.client_type} ")
