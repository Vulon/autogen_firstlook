from autogen_core.tools import FunctionTool
from enum import StrEnum


class ManagerRouteName(StrEnum):
    ASK_WORKER = "ask_worker"
    ASK_ALL_WORKERS = "ask_all_workers"
    ASK_USER = "ask_user"


async def ask_worker(worker_name: str, question: str) -> None:
    pass


async def ask_all_workers(question: str) -> None:
    pass


async def ask_user(question: str) -> None:
    pass


ask_worker_tool = FunctionTool(
    ask_worker,
    description="""
    Sends a message to the specific worker.
    :param worker_name: A worker name that will receive this message
    :param question: A string text, containing the question for the worker.
    """,
    name=ManagerRouteName.ASK_WORKER,
)

ask_all_workers_tool = FunctionTool(
    ask_all_workers,
    description="""
    Send a message to all workers.
    Every worker will receive a question, their responses will be returned collected before passing back to the manager agent.
    :param question: A string containing the question to all workers.
    """,
    name=ManagerRouteName.ASK_ALL_WORKERS,
)

ask_user_tool = FunctionTool(
    ask_user,
    description="""
    Send a question to the Human user for clarifications. 
    Use it, when you don't have enough details to properly process user's request. 
    :param question: A string that the human user will see.
    """,
    name=ManagerRouteName.ASK_USER,
)

MANAGER_TOOLS = [ask_worker_tool, ask_all_workers_tool, ask_user_tool]
