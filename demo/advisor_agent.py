from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.messages import HandoffMessage, TextMessage
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core.models import ChatCompletionClient
from datastore import CarIdCache
from messages import AdvisorMessage, TriageMessage, UserMessage
from tools import Tools
from typing_extensions import Annotated
from utils import print_core, print_route


class AdvisorAgent(RoutedAgent):

    pending_handfoffs = {}

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(
            description="An agent that specializes in advising a user in selecting the right car.",
        )
        print_core(f"Agent ({self.id}) initialized")

        self._agent = AssistantAgent(
            name="advisor_agent",
            model_client=model_client,
            tools=[Tools.get_available_cars, Tools.cache_carId],
            system_message=f"""
                You are a friendly and knowledgeable car selection agent dedicated to helping users find the car of their dreams. Your primary goal is to guide the user through a conversational journey that uncovers their true automotive needs and desires.
                Your agent_id is {self.id}.

                Key Details:

                You have access to a tool that retrieves a list of available cars when provided with specific parameters: car brand, year, and available budget.

                If the user does not specify any one of these details, consider that parameter open-ended, meaning you can assume any brand, year, or budget to start with.

                Ask the user clarifying questions about their preferences (e.g., what type of car they prefer, any specific features, performance or aesthetic priorities) while gently guiding them toward specifying details like brand, year, and budget.

                Use the available tools as soon as you have enough details to fetch relevant car options, and then discuss those options with the user.

                Make sure your conversation is engaging, informative, and tailored to the user's responses so that by the end, the user feels confident that you've helped them find the perfect car.

                Example Conversation Flow:

                Introduction & Warm-Up: Start with a friendly greeting and ask a few open-ended questions like, “What's most important to you in your next car—performance, comfort, style, or something else?”

                Information Gathering: Ask about any brand preferences, the desired model year or range, and their budget. For instance, “Do you have a favorite car brand or a particular year in mind? Also, what's your approximate budget for this new car?”

                Tool Utilization: Once you have enough information, inform the user that you're checking the latest available options. Retrieve the list of cars using the tool by passing the car brand, year, and budget (using defaults if any are missing).

                Recommendation & Engagement: Present the user with a tailored list of options. Provide insights into the features of each option, and ask follow-up questions like, “How do you feel about these choices?” or “Would you like to adjust any criteria?”

                Final Decision: Continue the conversation until the user identifies the car that truly feels like their dream car. Offer additional advice or alternative options if needed.

                Remember: The conversation should always focus on understanding the user's unique tastes and guiding them step-by-step toward a decision that best fits their lifestyle and preferences.
            """,
            reflect_on_tool_use=True,
            handoffs=[
                Handoff(
                    target="triage_agent",
                    description="Use it when the user provides a question that is out of the current discussion context.",
                    message="I'm sorry, I'm not able to help you with that. I'll redirect you to the right agent.",
                ),
                Handoff(
                    target="sales_agent",
                    description="Use it when the user provides a question that is related to ordering the car in discussion or when conversation turns into requesting info about existing orders. Be sure only one car is discussed and the cache_carId tool has been used.",
                    message="The user is interested in the car with car_id= {car_id}, find all the car details and then proceed with the order.",
                ),
            ],
        )

    @message_handler()
    async def handle_request(
        self, message: TriageMessage | UserMessage, ctx: MessageContext
    ) -> None:

        print_route(ctx.sender, self.id, message.content)

        response = await self._agent.on_messages(
            [TextMessage(content=message.content, source="user")],
            ctx.cancellation_token,
        )

        if isinstance(response.chat_message, HandoffMessage):
            match response.chat_message.target:
                case "sales_agent":
                    order_agent_instructions = response.chat_message.content.format(
                        car_id=CarIdCache.cache.pop(
                            str(self.id), -1
                        )  # not very safe, but for demo purposes
                    )

                    await self.send_message(
                        AdvisorMessage(content=order_agent_instructions),
                        AgentId(response.chat_message.target, self.id.key),
                    )
                case _:
                    await self.send_message(
                        TriageMessage(content=response.chat_message.content),
                        AgentId(response.chat_message.target, self.id.key),
                    )
        else:
            await self.send_message(
                AdvisorMessage(content=response.chat_message.content),
                AgentId("user_agent", self.id.key),
            )

        await self.send_message(
            TriageMessage(content=response.chat_message.content),
            AgentId("user_agent", self.id.key),
        )
