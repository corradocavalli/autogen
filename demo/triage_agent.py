from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.messages import HandoffMessage, TextMessage
from autogen_core import AgentId, MessageContext, RoutedAgent, TopicId, message_handler
from autogen_core.models import ChatCompletionClient
from messages import OrderUpdateMessage, TriageMessage, UserMessage
from utils import print_core, print_route


class TriageAgent(RoutedAgent):

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(
            description="An agent that specializes in handling user requests and handoff them to the proper agent."
        )

        print_core(f"Agent ({self.id}) initialized")

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

        response = await self._agent.on_messages(
            [TextMessage(content=message.content, source="user")],
            ctx.cancellation_token,
        )

        # print(
        #     f"[bold gray]({ctx.sender})[/bold gray]->[bold yellow]({self.id}) Received: {response}[/bold yellow]"
        # )

        # If agent request handoff, forwards the message to the target agent
        if isinstance(response.chat_message, HandoffMessage):
            match response.chat_message.target:
                case "advisor_agent":
                    await self.send_message(
                        TriageMessage(content=message.content),
                        AgentId(response.chat_message.target, self.id.key),
                    )
                case "sales_agent":
                    await self.send_message(
                        UserMessage(content=message.content),
                        AgentId(response.chat_message.target, self.id.key),
                    )
                case _:
                    await self.send_message(
                        TriageMessage(content=response.chat_message.content),
                        AgentId(response.chat_message.target, self.id.key),
                    )
        else:
            # If agent does not request handoff, send the response to the user
            await self.send_message(
                TriageMessage(content=response.chat_message.content),
                AgentId("user_agent", self.id.key),
            )
