import os

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


def get_model():
    return AzureOpenAIChatCompletionClient(
        azure_deployment=os.getenv("DEPLOYMENT"),
        model=os.getenv("MODEL"),
        api_version=os.getenv("VERSION"),
        azure_endpoint=os.getenv("ENDPOINT"),
        api_key=os.getenv("API_KEY"),
    )
