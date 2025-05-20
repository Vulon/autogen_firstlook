from asyncio import Lock
from collections import defaultdict

from autogen_core.models import LLMMessage


class MessageStore:
    def __init__(self):
        self._lock = Lock()

        self._all_messages: list[LLMMessage] = []
        self._worker_messages: dict[str, list[LLMMessage]] = defaultdict(list)

    async def add_public_message(self, message: LLMMessage) -> None:
        async with self._lock:
            self._all_messages.append(message)

    async def add_worker_message(self, message: LLMMessage, worker_name: str) -> None:
        async with self._lock:
            self._worker_messages[worker_name].append(message)

    async def get_all_messages(self) -> tuple[LLMMessage, ...]:
        async with self._lock:
            return tuple(self._all_messages)

    async def get_worker_messages(self, name: str) -> tuple[LLMMessage, ...]:
        async with self._lock:
            return tuple(self._worker_messages[name])
