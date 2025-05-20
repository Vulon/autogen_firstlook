from autogen_firstlook.settings import Settings
from autogen_firstlook.agents.worker_agent import WorkerAgent
from autogen_firstlook.agents.manager_agent import ManagerAgent
from autogen_firstlook.storage import MessageStore
from typing import Callable
from autogen_core.models import ChatCompletionClient


class AgentFactory:
    def __init__(self, settings: Settings, model_client: ChatCompletionClient):
        self.settings = settings
        self.message_store = MessageStore()
        self.model_client = model_client

    def create_manager_factory(
        self, worker_names: tuple[str, ...]
    ) -> Callable[[], ManagerAgent]:
        def spawn_agent() -> ManagerAgent:
            return ManagerAgent(
                description="An agent responsible for decomposing and planning implementation for new features",
                model_client=self.model_client,
                worker_names=worker_names,
                message_store=self.message_store,
            )

        return spawn_agent

    def create_worker_factory(self, worker_name: str) -> Callable[[], WorkerAgent]:
        def spawn_worker() -> WorkerAgent:
            return WorkerAgent(
                description="An agent that represents a developer. Designed to help the Manager agent",
                model_client=self.model_client,
                worker_name=worker_name,
                message_store=self.message_store,
            )

        return spawn_worker
