from autogen_firstlook.agents.manager_agent import ManagerAgent
from autogen_firstlook.agents.worker_agent import WorkerAgent
from autogen_firstlook.settings import Settings
from autogen_firstlook.client import create_model_client
from autogen_firstlook.factory import AgentFactory
from autogen_firstlook.communication.messages import FeatureMessage
from autogen_core.models import UserMessage
from autogen_core import (
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
)
from autogen_firstlook.communication.topics import USER_TOPIC, MANAGER_TOPIC


class Engine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model_client = create_model_client(self.settings)
        self.agent_factory = AgentFactory(self.settings, self.model_client)
        self.worker_names = tuple(
            f"Worker_{i}" for i in range(self.settings.worker_count)
        )

    async def run(self):
        runtime = SingleThreadedAgentRuntime()

        manager_agent_type = await ManagerAgent.register(
            runtime,
            type="manager",
            factory=self.agent_factory.create_manager_factory(self.worker_names),
        )
        await runtime.add_subscription(TypeSubscription(USER_TOPIC, manager_agent_type))

        for worker_name in self.worker_names:
            worker_agent_type = await WorkerAgent.register(
                runtime,
                type=worker_name,
                factory=self.agent_factory.create_worker_factory(worker_name),
            )
            await runtime.add_subscription(
                TypeSubscription(MANAGER_TOPIC, worker_agent_type)
            )

        runtime.start()
        user_message = UserMessage(
            content=input("Give description to the new feature: "), source="user"
        )
        await runtime.publish_message(
            FeatureMessage(message=user_message),
            topic_id=TopicId(USER_TOPIC, source="user"),
        )

        await runtime.stop_when_idle()
        await self.model_client.close()
