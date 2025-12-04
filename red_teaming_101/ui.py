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
    chat_history.append({"role": "assistant", "content": f"**Copilot**\n{assistant_response}"})

    # If solved, append a second assistant-only message (as empty user input)
    if res["solved"]:
        chat_history.append({
            "role": "assistant",
            "content": f"<div style='color:#b58900;font-weight:bold;'>Scorer message:</div>{res['score_message']}",
        })
        print(f"Lab solved! {chat_history[-1]}")

    return chat_history, ""


def load_lab_info(lab_title):
    info = "### Lab Information\n\nSelect a lab to see details."
    for lab in labs:
        if lab["challenge_title"] == lab_title:
            info = f"### {lab['challenge_title']}\n\n" \
                   f"**Goal:** {lab['goal']}\n\n" \
                   f"**Description:** {lab['description']}\n\n"
            if lab['desired_output']:
                info += f"**Desired Output:** {lab['desired_output']}\n\n"
            if "RagInput" in lab and "firstMessage" in lab["RagInput"]:
                # gr.Textbox.update(value=lab["RagInput"]["firstMessage"])
                info += f"**First Message to Try:** {lab["RagInput"]["firstMessage"]}\n\n"

            break

    # Reset chat + message box
    return info, [], ""


with gr.Blocks() as demo:
    gr.Markdown("## Minimal AI Red Teaming Playground")
    lab_dropdown = gr.Dropdown(
        choices=titles,
        value=titles[0],
        label="Select Lab"
    )
    starting_lab_info = load_lab_info(titles[0])[0]
    lab_info = gr.Markdown(starting_lab_info)
    chatbot = gr.Chatbot(
        label="chat",
        avatar_images=(None, "https://static.langfuse.com/cookbooks/gradio/hf-logo.png",),
    )
    prompt = gr.Textbox(max_lines=5, label="Your Message", placeholder="Type your prompt here...")
    prompt.submit(
        interact,
        [prompt, lab_dropdown, chatbot],
        [chatbot, prompt],
    )
    # Reset chat history on dropdown change
    lab_dropdown.change(
        load_lab_info,
        inputs=lab_dropdown,
        outputs=[lab_info, chatbot, prompt]
    )

demo.launch()
