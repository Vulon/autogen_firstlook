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
from autogen_firstlook.communication.messages import FeatureMessage, QuestionMessage
from autogen_firstlook.communication.topics import MANAGER_TOPIC
from autogen_firstlook.storage import MessageStore
from autogen_firstlook.logs import logger


class ManagerAgent(RoutedAgent):
    def __init__(
        self,
        description: str,
        model_client: ChatCompletionClient,
        worker_names: tuple[str, ...],
        message_store: MessageStore,
    ) -> None:
        super().__init__(description)

        self._model_client = model_client
        self._worker_names = worker_names
        self._message_store = message_store

    FEATURE_REQUEST_SYSTEM_PROMPT = """
    You are an agent manager. 
    You will receive a new feature request from the user. 
    Your job is to organize the discussion between the worker agents.   
    Formulate the questions to the workers to gather their feedback on this new feature.
    """

    @message_handler
    async def handle_new_request(
        self, message: FeatureMessage, ctx: MessageContext
    ) -> None:
        """
        Is triggered, when a user asks for a new feature.
        Manager should publish a message, asking every worker, what are their thoughts on this feature.
        Remember that we need to collect response from every worker.
        """
        logger.info(
            f"Received user's request for a new feature: {message.message.content}"
        )
        await self._message_store.add_public_message(message.message)
        system_message = SystemMessage(content=self.FEATURE_REQUEST_SYSTEM_PROMPT)
        llm_result = await self._model_client.create(
            messages=[system_message, message.message],
            cancellation_token=ctx.cancellation_token,
        )
        logger.info(f"Manager LLM response: {llm_result.content}")
        assistant_message = AssistantMessage(
            content=llm_result.content, source=self.id.key
        )

        await self.publish_message(
            QuestionMessage(message=assistant_message, context=[message.message]),
            topic_id=TopicId(MANAGER_TOPIC, source=self.id.key),
        )
