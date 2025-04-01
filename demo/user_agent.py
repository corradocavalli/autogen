from autogen_core import (
    AgentId,
    DefaultTopicId,
    DropMessage,
    MessageContext,
    RoutedAgent,
    message_handler,
)
from messages import (
    AdvisorMessage,
    OrderMessage,
    SessionStartMessage,
    TriageMessage,
    UserMessage,
    UserTerminationMessage,
)
from utils import print_assistant, print_core, print_info


class UserAgent(RoutedAgent):

    def __init__(self) -> None:
        super().__init__("Interactive user agent")
        print_core(f"Agent ({self.id}) initialized")

    @message_handler
    async def handle_session_start(
        self, message: SessionStartMessage, ctx: MessageContext
    ) -> None:

        user_input = input(
            f"\n({self.id.key}) Welcome to CarDream, how can i help you today? (type 'exit' to leave): "
        )
        if user_input == "exit":
            await self._terminate()
        else:
            user_message = UserMessage(content=user_input)
            await self.send_message(user_message, AgentId("triage_agent", self.id.key))

    @message_handler()
    async def handle_triage_request(
        self,
        message: TriageMessage | AdvisorMessage | OrderMessage,
        ctx: MessageContext,
    ) -> None:

        print_assistant(ctx.sender, self.id, message.content)

        user_input = input(f"\n({self.id.key}) Type your reply (or 'exit' to end): ")
        if user_input == "exit":
            await self._terminate()
        else:
            # we reply back to agent who requested user input
            user_message = UserMessage(content=user_input)
            await self.send_message(user_message, ctx.sender)

    # Handles the request to terminate the agent conversation
    async def _terminate(self) -> None:
        print_core(f"Terminating agent ({self.id})...")
        await self.publish_message(
            UserTerminationMessage(),
            DefaultTopicId(),
        )
