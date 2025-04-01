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
from rich import print


class UserAgent(RoutedAgent):

    def __init__(self) -> None:
        super().__init__("Interactive user agent")
        print(f"[bold gray]({self.id}) Initialized[/bold gray]")

    @message_handler
    async def handle_session_start(
        self, message: SessionStartMessage, ctx: MessageContext
    ) -> None:

        user_input = input(
            f"(Welcome to CarDream, how can i help you today? (type 'exit' to leave): "
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

        print(
            f"[bold gray]({ctx.sender})[/bold gray]->({self.id})[bold cyan] Received: {message.content}[/bold cyan]"
        )
        user_input = input(f"Enter your question (or type 'exit' to end): ")
        if user_input == "exit":
            await self._terminate()
        else:
            user_message = UserMessage(content=user_input)
            # we reply back to agent who requested user input
            await self.send_message(user_message, ctx.sender)

    # Handles the request to terminate the agent conversation
    async def _terminate(self) -> None:
        print(f"[bold green]Goodbye![/bold green]")
        await self.publish_message(
            UserTerminationMessage(),
            DefaultTopicId(),
        )
