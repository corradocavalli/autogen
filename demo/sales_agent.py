from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.messages import HandoffMessage, TextMessage
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core.models import ChatCompletionClient
from messages import AdvisorMessage, OrderMessage, TriageMessage, UserMessage
from tools import Tools
from utils import print_core, print_route


class SalesAgent(RoutedAgent):
    """
    Sales agent that specializes in handling user requests related to car orders.
    It uses a set of tools to perform operations such as creating, deleting, and retrieving orders.
    """

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(
            description="An agent that specializes in handling requests related to car orders.",
        )

        print_core(f"Agent ({self.id}) initialized")

        self._agent = AssistantAgent(
            name="order_management_agent",
            model_client=model_client,
            tools=[
                Tools.get_car,
                Tools.create_order,
                Tools.delete_order,
                Tools.get_order,
                Tools.get_orders,
                Tools.inform_after_sales_department,
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
            After successfully creating the order, you must invoke the tool `inform_after_sales_department` with the following details:
            - order id (as returned from the create_order tool)
                        
            Deleting an Order:

            Before proceeding with a deletion, always ask the user for a final confirmation.
            Ensure that the user explicitly confirms that they want to delete the order. 
            After successfully deleting the order, you must invoke the tool `inform_after_sales_department` with the following details:
            - order id
            
            Asking About Existing Orders:

            Request the customer name to fetch and display any existing orders related to that customer.

            Retrieving the List of Places Order:

            Ask for the customer's name in order to provide the list of places where orders have been made.     

            Informing the After Sales Department:

            Required Information:
            - order id
            - order status

            Each time a new order is created or an order is deleted, you must invoke the tool `inform_after_sales_department` to notify the after-sales department about the order status change.      

            Additional Guidelines:

            Always verify that all required information is provided before executing any operation.
            When information is missing, ask clear and concise follow-up questions to obtain the necessary details.
            Handle the conversation in a friendly, clear, and professional manner.
            Ensure that each operation is clearly confirmed with the user to avoid any miscommunication.

            If you encounter any issues, need further clarification, or require assistance, feel free to request a handoff to the proper agent.
            Kindly deny any requests that are not related to car orders or the tasks mentioned above.
            If the user is not interested in continuing the conversation, please use the handoff tool to transfer the conversation to the user agent.
            
            """,
            reflect_on_tool_use=True,
            handoffs=[
                Handoff(
                    target="triage_agent",
                    description="Use it when the user no longer needs assistance, the request has been resolved, the question is not relevant to an order or the user is not interested in continuing the conversation.",
                ),
                Handoff(
                    target="advisor_agent",
                    description="Use it when the user has question that is related to car advising or the user wishes some advising regarding ordering or considering a car like a car model or brand or seeing the available cars.",
                ),
            ],
        )

    @message_handler()
    async def handle_request(
        self, message: UserMessage | AdvisorMessage | TriageMessage, ctx: MessageContext
    ) -> None:
        print_route(ctx.sender, self.id, message.content)

        response = await self._agent.on_messages(
            [TextMessage(content=message.content, source="user")],
            ctx.cancellation_token,
        )

        if isinstance(response.chat_message, HandoffMessage):
            print_core(
                f"Agent ({self.id}) requested handoff to {response.chat_message.target}"
            )
            match response.chat_message.target:
                case "triage_agent":
                    await self.send_message(
                        UserMessage(content=message.content),
                        AgentId(response.chat_message.target, self.id.key),
                    )
                case "advisor_agent":
                    await self.send_message(
                        TriageMessage(content=message.content),
                        AgentId(response.chat_message.target, self.id.key),
                    )
        else:
            # If agent does not request handoff, send the request to the user agent
            await self.send_message(
                OrderMessage(content=response.chat_message.content),
                AgentId("user_agent", self.id.key),
            )
