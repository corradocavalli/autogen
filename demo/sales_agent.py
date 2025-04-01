from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.messages import HandoffMessage, TextMessage
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core.models import ChatCompletionClient
from messages import AdvisorMessage, OrderMessage, TriageMessage, UserMessage
from rich import print
from tools import Tools


class SalesAgent(RoutedAgent):

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(
            description="An agent that specializes in handling requests related to car orders.",
        )
        print(f"[bold gray]({self.id}) Initialized[/bold gray]")

        self._agent = AssistantAgent(
            name="order_management_agent",
            model_client=model_client,
            tools=[
                Tools.get_car,
                Tools.create_order,
                Tools.delete_order,
                Tools.get_order,
                Tools.get_orders,
                Tools.inform_user_about_order_status,
            ],
            system_message=f""""
            You are a specialized assistant responsible for handling conversations related to car orders.
            Your primary tasks include creating orders, deleting orders, checking existing orders, and retrieving the list of places where orders have been made. Follow these guidelines:

            Creating an Order:

            Required Information:
            - id of the car to order
            - Customer name
            - Customer email            
            
            Before creating the order, ask the user for a confirmation of the order details and ask to confirm by typing "yes" or "no".
            If the user confirms, proceed with the order creation.
            If the user does not confirm, ask them if they would like to provide any additional information or cancel the order.                              

            Deleting an Order:

            Before proceeding with a deletion, always ask the user for a final confirmation.
            Ensure that the user explicitly confirms that they want to delete the order.                     

            Asking About Existing Orders:

            Request the customer name to fetch and display any existing orders related to that customer.

            Retrieving the List of Places Order:

            Ask for the customer's name in order to provide the list of places where orders have been made.            

            Additional Guidelines:

            Always verify that all required information is provided before executing any operation.
            When information is missing, ask clear and concise follow-up questions to obtain the necessary details.
            Handle the conversation in a friendly, clear, and professional manner.
            Ensure that each operation is clearly confirmed with the user to avoid any miscommunication.

            If you encounter any issues, need further clarification, or require assistance, feel free to request a handoff to the proper agent.
            Kindly deny any requests that are not related to car orders or the tasks mentioned above.
            If the user is not interested in continuing the conversation, please use the handoff tool to transfer the conversation to the user agent.

            IMPORTANT: After each order creation or deletetion inform the user a notification has been sent to their email by checking the returned value of the 'inform_user_about_order_status' tool.
            """,
            reflect_on_tool_use=True,
            handoffs=[
                Handoff(
                    target="user_agent",
                    description="Use it when the user no longer needs assistance, the request has been resolved, or the user is not interested in continuing the conversation.",
                ),
                Handoff(
                    target="advisor_agent",
                    description="Use it when the user generates a question that might require advising or information about a specific car or just need additional help in selecting a car.",
                ),
            ],
        )

    @message_handler()
    async def handle_request(
        self, message: UserMessage | AdvisorMessage | TriageMessage, ctx: MessageContext
    ) -> None:
        print(
            f"[bold gray]({ctx.sender})[/bold gray]->({self.id})[bold yellow] Received: {message.content}[/bold yellow]"
        )

        response = await self._agent.on_messages(
            [TextMessage(content=message.content, source="user")],
            ctx.cancellation_token,
        )

        # print(f"[bold yellow]({self.id}) Response: {response}[/bold yellow]")

        # If agent request handoff, send the message to the target agent
        if isinstance(response.chat_message, HandoffMessage):
            match response.chat_message.target:
                case "advisor_agent":
                    await self.send_message(
                        TriageMessage(
                            content=message.content
                        ),  # we forward the original message
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
                OrderMessage(content=response.chat_message.content),
                AgentId("user_agent", self.id.key),
            )
