from autogen_core import (
    MessageContext,
    RoutedAgent,
    TopicId,
    message_handler,
)
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    SystemMessage,
)
from autogen_firstlook.communication.messages import QuestionMessage, ResponseMessage
from autogen_firstlook.communication.topics import WORKER_TOPIC
from autogen_firstlook.storage import MessageStore
from autogen_firstlook.logs import logger


class WorkerAgent(RoutedAgent):
    QUESTION_SYSTEM_PROMPT = """
    You are a worker agent. 
    The user has submitted a request for a new feature. 
    The Manager agent requires your help. 
    Answer any questions from the Manager agent.
    """

    def __init__(
        self,
        description: str,
        model_client: ChatCompletionClient,
        worker_name: str,
        message_store: MessageStore,
    ) -> None:
        super().__init__(description)

        self._model_client = model_client
        self._message_store = message_store
        self._name = worker_name

    @message_handler
    async def handle_question(
        self, message: QuestionMessage, ctx: MessageContext
    ) -> None:
        messages_history = self._message_store.get_worker_messages(self._name)
        if not messages_history:
            for context_message in message.context:
                await self._message_store.add_worker_message(
                    context_message, self._name
                )

        messages_history = await self._message_store.get_worker_messages(self._name)
        logger.info(f"Retrieved worker messages: {messages_history}")
        system_message = SystemMessage(content=self.QUESTION_SYSTEM_PROMPT)

        input_messages = [system_message] + list(messages_history) + [message.message]

        llm_result = await self._model_client.create(
            messages=input_messages,
            cancellation_token=ctx.cancellation_token,
        )
        logger.info(f"Worker LLM response: {llm_result}. Content: {llm_result.content}")
        response = ResponseMessage(
            message=AssistantMessage(content=llm_result.content, source=self.id.key)
        )

        await self.publish_message(
            response,
            topic_id=TopicId(WORKER_TOPIC, source=self.id.key),
        )
