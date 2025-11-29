import gradio as gr
import requests

from loader import load_challenges

API_URL = "http://127.0.0.1:8000/message"

labs = load_challenges()
titles = [lab["challenge_title"] for lab in labs]


def interact(user_message, lab_title, chat_history):
    print(f"Lab: {lab_title} | Message: {user_message}")
    payload = {
        "lab_title": lab_title,
        "user_message": user_message
    }
    res = requests.post(API_URL, json=payload).json()
    print(f"FastAPI Response: {res}")
    assistant_response = res["reply"]

    # Append a single pair: [user, assistant]
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": assistant_response})

    # If solved, append a second assistant-only message (as empty user input)
    if res["solved"]:
        chat_history.append(("", res["score_message"]))

    return chat_history, ""


def reset_lab(lab_title):
    return [], ""


with gr.Blocks() as demo:
    gr.Markdown("## Minimal Python Red Teaming Playground")
    lab_dropdown = gr.Dropdown(
        choices=titles,
        value=titles[0],
        label="Select Lab"
    )
    chatbot = gr.Chatbot()
    # chatbot = gr.Chatbot(
    #     label="chat",
    #     type="messages",
    #     show_copy_button=True,
    #     avatar_images=(None, "https://static.langfuse.com/cookbooks/gradio/hf-logo.png",),
    # )
    # prompt = gr.Textbox(max_lines=1, label="Chat Message")
    # prompt.submit(respond, [prompt, chatbot], [chatbot])
    msg = gr.Textbox(label="Your Message")
    msg.submit(
        interact,
        [msg, lab_dropdown, chatbot],
        [chatbot, msg],
    )
    # Reset chat history on dropdown change
    lab_dropdown.change(reset_lab, lab_dropdown, [chatbot, msg])

demo.launch()
