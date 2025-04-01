from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import MessageContext, RoutedAgent, message_handler, type_subscription
from autogen_core.models import ChatCompletionClient
from messages import OrderUpdateMessage
from tools import Tools
from utils import print_core, print_notification, print_route


@type_subscription(topic_type="order_update")
class AfterSalesAgent(RoutedAgent):
    """
    After-sales agent that specializes in handling after-sales operations.
    It uses a set of tools to perform operations such as looking up orders.
    This agent shows an example of how to use broadcasting messages to multiple agents.
    """

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(
            description="An agent that specializes in handling after-sales operations.",
        )

        print_core(f"Agent ({self.id}) initialized")

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
            CardDream Service Team
            """,
            reflect_on_tool_use=True,
        )

    # this is the handler for the order update topic
    @message_handler()
    async def handle_topic(
        self, message: OrderUpdateMessage, ctx: MessageContext
    ) -> None:
        """
        Handles the order update message and forwards it to the after-sales agent.
        """

        print_route(ctx.sender, self.id, message.order_id)

        query = f"The following order has been updated: {message.order_id}"
        response = await self._agent.on_messages(
            [TextMessage(content=query, source="user")],
            ctx.cancellation_token,
        )

        # we just print the response here, but in a real scenario we would send it to the customer
        # using the email service.
        print_notification(
            ctx.sender,
            self.id,
            f"Sending notification...\n{response.chat_message.content}",
        )
