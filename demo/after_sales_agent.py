from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import (
    AgentId,
    MessageContext,
    RoutedAgent,
    message_handler,
    type_subscription,
)
from autogen_core.models import ChatCompletionClient
from messages import OrderUpdateMessage
from pydantic import BaseModel
from rich import print
from tools import Tools


@type_subscription(topic_type="order_update")
class AfterSalesAgent(RoutedAgent):

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(
            description="An agent that specializes in handling after-sales operations.",
        )
        print(f"[bold gray]({self.id}) Initialized[/bold gray]")

        self._agent = AssistantAgent(
            name="communication_agent",
            model_client=model_client,
            tools=[Tools.lookup_order],
            system_message=f""""
            You are a helpful assistant that can handle after-sales operations.
            Your goal is to craft emails informing the customer about the order status.

            use the following template to construct the email:

            Dear <customer_name>,

            We'd like to inform you that your order '<order_id>' placed on <order_date> for the car <car_brand> <car_model> has been updated to '<status>'.

            Best regards,
            Customer Service Team
            """,
            reflect_on_tool_use=True,
        )

    # this is the handler for the order update topic
    @message_handler()
    async def handle_topic(
        self, message: OrderUpdateMessage, ctx: MessageContext
    ) -> None:
        print(
            f"[bold gray]({ctx.sender})[/bold gray]->({self.id})[bold yellow] Received: {message.order_id}-{message.status}[/bold yellow]"
        )

        query = f"The following order has been updated: {message.order_id}"
        response = await self._agent.on_messages(
            [TextMessage(content=query, source="user")],
            ctx.cancellation_token,
        )

        print(
            f"[bold cyan italic]({self.id}) e-email: {response.chat_message.content}[/bold cyan italic]"
        )
