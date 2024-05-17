import ollama
import streamlit as st
import asyncio
import time
import base64
from openai import AsyncOpenAI
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.bottom_container import bottom
import random
from utils import style_page, clear_everything, meta_formatting
import uuid

from functools import partial
import structlog
from pathlib import Path

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.WriteLoggerFactory(
        file=Path("app").with_suffix(".log").open("at")
    ),
)
logger = structlog.get_logger()

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
    prompt = st.chat_input("Message Ollama")
    with stylable_container(
        key="green_button",
        css_styles="""
            button {
                background-color: #CCCCCC;
                color: black;
                border-radius: 10px;
                width: 50%
            }
            """,
    ):
        next_round = st.button("Next Round")
        if next_round:
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
    logger.info("Request starts", id=request_id, model=model, prompt=message_history[-1]["content"])
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
    logger.info("Request finished", id=request_id, model=model, prompt=message_history[-1]["content"])
                
    message_history.append({"role": "assistant", "content": streamed_text})

@st.experimental_dialog("Cast your vote")
def vote():
    st.write(f"Which model was best?")
    item = st.radio("Which model was best?", options=["Model 1", "Model 2", "Neither"])
    if st.button("Submit"):
        st.session_state.vote = {"item": item}
        st.rerun()

async def main():
    await asyncio.gather(
        run_prompt(body_1,  model=model_1, message_history=st.session_state.messages1),
        run_prompt(body_2,  model=model_2, message_history=st.session_state.messages2)
    )
    await asyncio.sleep(0.5)
    if "vote" not in st.session_state:
        vote()

if prompt:
    if prompt == "":
        st.warning("Please enter a prompt")
    else:        
        st.session_state.messages1.append({"role": "user", "content": prompt})
        st.session_state.messages2.append({"role": "user", "content": prompt})
        asyncio.run(main())
