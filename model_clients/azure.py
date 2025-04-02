import os

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


def get_model():
    """
    Get the model client for Azure OpenAI.

    You can modify the code here to use a different model clients like
    OpenAI, Azure AI Foundry, Anthropic, Ollama, Gemini or even Semantic Kernel.
    """
    return AzureOpenAIChatCompletionClient(
        azure_deployment=os.getenv("DEPLOYMENT"),
        model=os.getenv("MODEL"),
        api_version=os.getenv("VERSION"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_key=os.getenv("API_KEY"),
    )
