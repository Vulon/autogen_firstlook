from pydantic import BaseModel
from autogen_core.models import UserMessage, AssistantMessage, LLMMessage


class FeatureMessage(BaseModel):
    message: UserMessage


class UserResponseMessage(BaseModel):
    message: UserMessage


class QuestionMessage(BaseModel):
    message: AssistantMessage
    context: list[LLMMessage]
    is_round_question: bool


class ResponseMessage(BaseModel):
    message: AssistantMessage
    is_round_question: bool
