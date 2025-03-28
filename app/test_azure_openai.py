# Run this to test your azure openai connection
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Get credentials
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")

print(f"Testing connection to {endpoint} using deployment {deployment}")

# Create client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=endpoint,
    api_version=api_version
)

# Test basic completion
try:
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=50
    )
    print(f"Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {str(e)}")