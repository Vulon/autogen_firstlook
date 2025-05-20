import json

from autogen_core import (
    MessageContext,
    RoutedAgent,
    TopicId,
    message_handler,
    FunctionCall,
    AgentId,
)
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    SystemMessage,
    UserMessage,
)
from autogen_firstlook.communication.messages import (
    FeatureMessage,
    QuestionMessage,
    ResponseMessage,
)
from autogen_firstlook.communication.topics import MANAGER_TOPIC
from autogen_firstlook.storage import MessageStore
from autogen_firstlook.logs import logger
from autogen_firstlook.tools.manager_tools import MANAGER_TOOLS, ManagerRouteName


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

    ROUTING_SYSTEM_PROMPT = """
    You are an agent manager. 
    
    - Goal - 
    Decide the next action to take
    
    - Details - 
    You received a request from the user for a new feature. 
    You need to decompose the work into small tasks. 
    You have several worker agents that can help you with that task.    
    As a Manager agent you have to use function calling to decide the next action to take.
    Always call one function at a time. 
    
    - Workers - 
    {workers}    
    """

    @message_handler
    async def handle_new_request(
        self, message: FeatureMessage, ctx: MessageContext
    ) -> None:
        """
        Is triggered, when a user asks for a new feature.
        """
        logger.info(
            f"Received user's request for a new feature: {message.message.content}"
        )
        await self._message_store.add_public_message(message.message)
        await self._run_agentic_routing(ctx)

    async def _send_message_to_worker(self, worker_name: str, question: str) -> None:
        assistant_message = AssistantMessage(
            content=f"Manager: {question}", source=self.id.key
        )
        await self._message_store.add_public_message(assistant_message)
        message = QuestionMessage(
            message=assistant_message, is_round_question=False, context=[]
        )
        agent_id = AgentId(worker_name, "default")
        await self.send_message(message, agent_id)

    async def _send_message_to_all_workers(self, question: str) -> None:
        await self._message_store.start_new_round()
        assistant_message = AssistantMessage(
            content=f"Manager: {question}", source=self.id.key
        )
        await self._message_store.add_public_message(assistant_message)
        message = QuestionMessage(
            message=assistant_message, is_round_question=True, context=[]
        )
        await self.publish_message(
            message,
            topic_id=TopicId(MANAGER_TOPIC, source=self.id.key),
        )

    async def _send_message_to_user(self, question: str) -> None:
        print("Question for user: ")
        print(question)
        response = input("User response: ")
        user_message = UserMessage(content=response, source="user")
        await self._message_store.add_public_message(user_message)

        # message = UserResponseMessage(message=user_message)

        raise NotImplementedError("Implement this function in a separate agent")

    async def _run_agentic_routing(self, ctx: MessageContext):
        """
        Let the agent decide, what action to do next.
        """
        system_message = SystemMessage(
            content=self.ROUTING_SYSTEM_PROMPT.format(
                workers="\n".join(self._worker_names)
            )
        )
        messages = await self._message_store.get_all_messages()

        llm_result = await self._model_client.create(
            messages=[system_message] + list(messages),
            tools=MANAGER_TOOLS,
            cancellation_token=ctx.cancellation_token,
        )
        if isinstance(llm_result.content, str):
            logger.info(f"Manager's final response: {llm_result.content}")
            return
        if len(llm_result.content) == 0:
            raise ValueError("TODO: We should try calling the LLM again here")
        for call in llm_result.content:
            call: FunctionCall
            arguments = json.loads(call.arguments)
            logger.info(f"Processing tool call: {call.name}. Arguments: {arguments}")
            match call.name:
                case ManagerRouteName.ASK_WORKER:
                    await self._send_message_to_worker(
                        arguments["worker_name"], arguments["question"]
                    )
                case ManagerRouteName.ASK_ALL_WORKERS:
                    await self._send_message_to_all_workers(arguments["question"])
                case ManagerRouteName.ASK_USER:
                    await self._send_message_to_user(arguments["question"])

    @message_handler(match=lambda msg, ctx: msg.is_round_question)
    async def handle_worker_round_response(
        self, message: ResponseMessage, ctx: MessageContext
    ) -> None:
        """
        This is triggered, when a worker publishes a response to the manager's question.
        """
        logger.info("Manager. Handling worker round response")
        await self._message_store.add_message_to_round(message.message)

        round_messages = await self._message_store.get_round_messages()

        if len(round_messages) >= len(self._worker_names):
            # We've collected responses from all workers.
            await self._run_agentic_routing(ctx)

    @message_handler(match=lambda msg, ctx: not msg.is_round_question)
    async def handle_direct_worker_response(
        self, message: ResponseMessage, ctx: MessageContext
    ) -> None:
        logger.info("Handling direct worker response")
        await self._run_agentic_routing(ctx)
