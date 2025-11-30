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
        return answer
    except BadRequestError as e:
        # Extract Azure filter info
        reason = None
        try:
            inner = e.json_body.get("error", {}).get("innererror", {})
            reason = inner.get("code", "content_filter")
        except Exception:
            pass

        # Always return 200 with an assistant-friendly message
        return {
            "role": "assistant",
            "content": (
                "Your previous message triggered Azure OpenAI’s safety filters. "
                "Please rewrite your request using safer phrasing."
            ),
            "error_type": "azure_policy_violation",
            "details": reason,
        }
    except Exception as e:
        err_msg = f"[Azure OpenAI] Error during chat completion: {e}"
        print(err_msg)
        return err_msg
