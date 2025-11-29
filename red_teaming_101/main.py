from dotenv import load_dotenv

load_dotenv()  # Load it before anything else that might need the env vars (like azure_client)

from fastapi import FastAPI
from pydantic import BaseModel

from loader import get_lab_by_title
from azure_client import chat

app = FastAPI()

# runtime state: store only the active lab
active_lab = None


class UserInput(BaseModel):
    lab_title: str
    user_message: str


@app.post("/message")
async def message(user_input: UserInput):
    global active_lab

    if active_lab is None or active_lab.title != user_input.lab_title:
        # lab switching = full reset
        # Load the requested lab
        active_lab = get_lab_by_title(user_input.lab_title)
        if active_lab is None:
            return {"error": "Lab not found"}
        active_lab.reset_history()

    # append user message
    active_lab.add_message("user", user_input.user_message)

    # call Azure OpenAI
    model_response = chat(active_lab.get_messages())

    # append assistant reply
    active_lab.add_message("assistant", model_response)
    # scoring
    solved, score_msg = active_lab.evaluate(model_response)

    return {
        "reply": model_response,
        "solved": solved,
        "score_message": score_msg
    }
