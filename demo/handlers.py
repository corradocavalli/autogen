from typing import Any

from autogen_core import (
    AgentId,
    DefaultInterventionHandler,
    DropMessage,
    MessageContext,
)
from messages import UserTerminationMessage


# Represents a handler that listens for user termination messages
class UserTerminationHandler(DefaultInterventionHandler):
    def __init__(self) -> None:
        self._termination_value: UserTerminationMessage | None = None

    async def on_publish(self, message: Any, *, message_context: MessageContext) -> Any:
        if isinstance(message, UserTerminationMessage):
            self._termination_value = message
        return message

    async def on_response(
        self, message: Any, *, sender: AgentId, recipient: AgentId | None
    ) -> Any | type[DropMessage]:
        return UserTerminationMessage()

    @property
    def termination_value(self) -> UserTerminationMessage | None:
        return self._termination_value

    @property
    def has_terminated(self) -> bool:
        return self._termination_value is not None
