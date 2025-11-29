import os

from openai import AzureOpenAI

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

client = AzureOpenAI(
    api_version="2024-06-01",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)


def chat(prompt):
    print(f"[Azure OpenAI] Sending messages: {prompt}")
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=prompt
    )
    answer = response.choices[0].message.content
    print(f"[Azure OpenAI] Received response: {answer}")
    return answer
