from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.messages import HandoffMessage, TextMessage
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core.models import ChatCompletionClient
from messages import TriageMessage, UserMessage
from utils import print_core, print_route


class TriageAgent(RoutedAgent):
    """
    Triage agent that specializes in handling user requests and forwarding them to the appropriate agent.
    """

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(
            description="An agent that specializes in handling user requests and handoff them to the proper agent."
        )

        print_core(f"Agent ({self.id}) initialized")

        # We rely on the AssistantAgent to handle the triage process since it offers a nice handoff mechanism.
        self._agent = AssistantAgent(
            name="triage_agent",
            model_client=model_client,
            handoffs=[
                Handoff(
                    target="user_agent",
                    description="Use it when the user provides a question that is not relevant to car ordering, advising, availability or related to a previous car order.",
                    message="I'm sorry, I'm not able to help you with that.",
                ),
                Handoff(
                    target="advisor_agent",
                    description="Use it when the user provides a question that involves a conversation about a car or the user wishes some advising regarding ordering or considering a car.",
                ),
                Handoff(
                    target="sales_agent",
                    description="Use it when the user provides a question that involves a conversation about a an existing order or he wishes to cancel an order.",
                ),
            ],
            system_message=f""""
            "You are an assistant whose role is to triage user requests and handoff them to the proper agent.
            If you need more information about the user request, you can ask the user for more details.
            """,
            reflect_on_tool_use=True,
        )

    @message_handler()
    async def handle_request(self, message: UserMessage, ctx: MessageContext) -> None:
        print_route(ctx.sender, self.id, message.content)
        """
        Handles the request from the User Agent and uses the internal assistant to decide how to handle it.
        """

        response = await self._agent.on_messages(
            [TextMessage(content=message.content, source="user")],
            ctx.cancellation_token,
        )

        # If agent request handoff, forwards the message to the target agent
        if isinstance(response.chat_message, HandoffMessage):
            match response.chat_message.target:
                # The user probably want to ask about a car or needs some advising
                case "advisor_agent":
                    response = await self.send_message(
                        TriageMessage(content=message.content),
                        AgentId(response.chat_message.target, self.id.key),
                    )
                # The user probably wants to cancel an order or ask about an existing order
                case "sales_agent":
                    await self.send_message(
                        UserMessage(content=message.content),
                        AgentId(response.chat_message.target, self.id.key),
                    )
                case _:
                    # The user probably has provided a question that is not relevant.
                    await self.send_message(
                        TriageMessage(content=response.chat_message.content),
                        AgentId(response.chat_message.target, self.id.key),
                    )
        else:
            # In case the agent does not request handoff, send the response back to user agent
            # to let the user agent continue the conversation
            await self.send_message(
                TriageMessage(content=response.chat_message.content),
                AgentId("user_agent", self.id.key),
            )
