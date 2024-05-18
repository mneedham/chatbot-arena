import ollama
import streamlit as st
import asyncio
import time
import base64
from openai import AsyncOpenAI
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.bottom_container import bottom
import random
from utils import style_page, clear_everything, meta_formatting, create_logger
import uuid

from functools import partial

voting_logger = create_logger("voting", "voting.log")
requests_logger = create_logger("requests", "requests.log")

title = "Ollama Chatbot Arena"
st.set_page_config(page_title=title, layout="wide")
style_page()
st.title(title)

if not "messages1" in st.session_state:
    st.session_state.messages1 = []

if not "messages2" in st.session_state:
    st.session_state.messages2 = []

client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ignore-me")

models = [
    m['name'] 
    for m in ollama.list()["models"]  
    if m["details"]["family"] in ["llama", "gemma"] and m["details"]["parameter_size"] in ['3B', '4B', '7B', '8B', '9B']
]
models = ["gemma:latest", 'gemma:2b', 'llama3:latest', 'mistral:latest', 'phi3:latest', 'zephyr:latest']

if not "selected_models" in st.session_state or len(st.session_state.selected_models) == 0:
    st.session_state.selected_models = random.sample(models, 2)

model_1, model_2 = st.session_state.selected_models

col1, col2 = st.columns(2)

meta_1 = col1.empty()
meta_2 = col2.empty()

meta_1.write(f"## :blue[Model 1]")
meta_2.write(f"## :red[Model 2]")

body_1 = col1.empty()
body_2 = col2.empty()

with bottom():
    voting_buttons = st.empty()
    prompt = st.chat_input("Message Ollama")
    with stylable_container(
        key="next_round_button",
        css_styles="""
            button {
                background-color: #CCCCCC;
                color: black;
                border-radius: 10px;
                width: 50%
            }
            """,
    ):
        new_round = st.button("New Round", key="new_round")
        if new_round:
            clear_everything()
            

# Render existing state
if "vote" in st.session_state:
    meta_1.write(partial(meta_formatting, "blue", "Model 1")(model_1))
    meta_2.write(partial(meta_formatting, "red", "Model 2")(model_2))

if len(st.session_state.messages1) > 0 or len(st.session_state.messages2) > 0:
    with body_1.container():
        for message in st.session_state.messages1:
            chat_entry = st.chat_message(name=message['role'])
            chat_entry.write(message['content'])

    with body_2.container():
        for message in st.session_state.messages2:
            chat_entry = st.chat_message(name=message['role'])
            chat_entry.write(message['content'])

async def run_prompt(placeholder, model, message_history):
    with placeholder.container():
        for message in message_history:
            chat_entry = st.chat_message(name=message['role'])
            chat_entry.write(message['content'])
        assistant = st.chat_message(name="assistant")

        with open("images/loading-gif.gif", "rb") as file:
            contents = file.read()
            data_url = base64.b64encode(contents).decode("utf-8")

        assistant.html(f"<img src='data:image/gif;base64,{data_url}' class='spinner' width='25' />")

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *message_history
    ]

    request_id = str(uuid.uuid4())
    requests_logger.info("Request starts", id=request_id, model=model, prompt=message_history[-1]["content"])
    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    streamed_text = ""
    async for chunk in stream:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content is not None:
            streamed_text = streamed_text + chunk_content
            with placeholder.container():
                for message in message_history:
                    chat_entry = st.chat_message(name=message['role'])
                    chat_entry.write(message['content'])
                assistant = st.chat_message(name="assistant")
                assistant.write(streamed_text)    
    requests_logger.info("Request finished", id=request_id, model=model, response=streamed_text)
                
    message_history.append({"role": "assistant", "content": streamed_text})


def do_vote(choice):
    st.session_state.vote = {"choice": choice}
    voting_logger.info("Vote", model1=model_1, model2=model_2, choice=choice)

    if choice == "model1":
        vote_choice = model_1
    elif choice == "model2":
        vote_choice = model_2
    else:
        vote_choice = "Both the same"

    st.toast(f"""Vote cast: **{vote_choice}**  
    Click 'new round' to compare another two models.""", icon='🗳️')

def vote():
    with voting_buttons.container():
        with stylable_container(
            key="voting_button",
            css_styles="""
                button {
                    background-color: #CCCCCC;
                    color: black;
                    border-radius: 10px;
                    width: 100%;
                }

                """,
        ):
            col1, col2, col3 = st.columns(3)
            model1 = col1.button("Model 1 👈", key="model1", on_click=do_vote, args=["model1"])
            model2 = col2.button("Model 2 👉", key="model2", on_click=do_vote, args=["model2"])
            neither = col3.button("Both the same 🤝", key="same", on_click=do_vote, args=["same"])

async def main():
    await asyncio.gather(
        run_prompt(body_1,  model=model_1, message_history=st.session_state.messages1),
        run_prompt(body_2,  model=model_2, message_history=st.session_state.messages2)
    )
    if "vote" not in st.session_state:
        vote()

if prompt:
    if prompt == "":
        st.warning("Please enter a prompt")
    else:        
        st.session_state.messages1.append({"role": "user", "content": prompt})
        st.session_state.messages2.append({"role": "user", "content": prompt})
        asyncio.run(main())
