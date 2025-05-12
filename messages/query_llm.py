import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file in the root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
# Retrieve Azure OpenAI configuration from environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") 

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)

def send_query_to_llm(msgs:list) -> str:
    try:
        response = client.chat.completions.create(
            model=deployment_name,  # Use your deployment name here
            messages=msgs,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM Error] {str(e)}"
