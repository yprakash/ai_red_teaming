import os

from openai import AzureOpenAI, BadRequestError

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

client = AzureOpenAI(
    api_version="2024-06-01",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)


def chat(prompt):
    try:
        print(f"[Azure OpenAI] Sending messages: {prompt}\n")
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=prompt
        )
        answer = response.choices[0].message.content
        print(f"[Azure OpenAI] Received response: {answer}\n")
        return True, answer
    except BadRequestError as e:
        err_msg = f"You'll have to start a new chat session because of an BadRequestError from [Azure OpenAI]: {e}"
        print(err_msg)
        return False, err_msg
    except Exception as e:
        err_msg = f"[Azure OpenAI] Error during chat completion: {e}"
        print(err_msg)
        return False, err_msg
