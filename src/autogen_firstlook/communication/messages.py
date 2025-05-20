from pydantic import BaseModel
from autogen_core.models import UserMessage, AssistantMessage, LLMMessage


class FeatureMessage(BaseModel):
    message: UserMessage


class QuestionMessage(BaseModel):
    message: AssistantMessage
    context: list[LLMMessage]


class ResponseMessage(BaseModel):
    message: AssistantMessage
