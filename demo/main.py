import sys

sys.path.append("..")
import asyncio

from advisor_agent import AdvisorAgent
from autogen_core import AgentId, SingleThreadedAgentRuntime, TopicId
from autogen_core.models import ChatCompletionClient
from datastore import CarDB
from handlers import UserTerminationHandler
from messages import OrderUpdateMessage, SessionStartMessage
from rich import print
from tools import Tools
from triage_agent import TriageAgent
from user_agent import UserAgent

from cardream_demo.after_sales_agent import AfterSalesAgent
from cardream_demo.sales_agent import SalesAgent
from model_clients.azure import get_model


async def register_agents(
    runtime: SingleThreadedAgentRuntime, model_client: ChatCompletionClient
):
    await TriageAgent.register(
        runtime,
        type="triage_agent",
        factory=lambda: TriageAgent(model_client=model_client),
    )

    await UserAgent.register(runtime, type="user_agent", factory=lambda: UserAgent())

    await AdvisorAgent.register(
        runtime,
        type="advisor_agent",
        factory=lambda: AdvisorAgent(model_client=model_client),
    )

    await SalesAgent.register(
        runtime,
        type="sales_agent",
        factory=lambda: SalesAgent(model_client=model_client),
    )

    await AfterSalesAgent.register(
        runtime,
        type="after_sale_agent",
        factory=lambda: AfterSalesAgent(model_client=model_client),
    )


async def send_session_message(
    runtime: SingleThreadedAgentRuntime, session_id: str
) -> None:
    await runtime.send_message(SessionStartMessage(), AgentId("user_agent", session_id))


async def main():
    # Initializes the database if it doesn't exist
    CarDB().init()

    print("[bold magenta italic]Starting the runtime...[/bold magenta italic]")

    # Create the runtime with a termination handler
    # This handler will handle the termination of the runtime
    termination_handler = UserTerminationHandler()
    runtime = SingleThreadedAgentRuntime(intervention_handlers=[termination_handler])
    Tools.runtime = runtime

    # Get the LLM client
    model_client = get_model()
    # Register the agents
    await register_agents(runtime, model_client)

    runtime.start()

    # Start the session
    session_ids = ["1"]
    await asyncio.gather(
        *(send_session_message(runtime, session_id) for session_id in session_ids)
    )

    await runtime.stop_when(lambda: termination_handler.has_terminated)

    # Close the runtime freeing up resources
    await runtime.close()
    print("[bold magenta italic]Runtime stopped[/bold magenta italic]")


if __name__ == "__main__":
    asyncio.run(main())
