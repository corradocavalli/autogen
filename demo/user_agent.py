from autogen_core import (
    AgentId,
    DefaultTopicId,
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
from utils import print_assistant, print_core, print_route


class UserAgent(RoutedAgent):
    """
    User agent that interacts with the user and forwards messages to the appropriate agent.
    """

    def __init__(self) -> None:
        super().__init__("Interactive user agent")
        print_core(f"Agent ({self.id}) initialized")
        self.is_terminated = False

    @message_handler
    async def handle_session_start(
        self, message: SessionStartMessage, ctx: MessageContext
    ) -> None:
        """
        Handles the session start message and initiates the conversation with the user.
        """

        print_route(
            self.id,
            ctx.sender,
            "User session started",
        )
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
        """
        Handles the request from the triage agent or advisor agent and forwards it to the user.
        """

        if self.is_terminated:
            return

        print_assistant(ctx.sender, self.id, message.content)

        user_input = input(f"\n({self.id.key}) Type your reply (or 'exit' to end): ")
        if user_input == "exit":
            await self._terminate()
            self.is_terminated = True
        else:
            # Once the user provided some input we reply back to agent who requested user input
            # to let the agent conversation continue
            user_message = UserMessage(content=user_input)
            await self.send_message(user_message, ctx.sender)

    async def _terminate(self) -> None:
        """
        Handles the termination of the agent conversation.
        """
        print_core(f"Terminating agent ({self.id})...")
        await self.publish_message(
            UserTerminationMessage(),
            DefaultTopicId(),
        )
