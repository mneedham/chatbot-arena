import ollama
import streamlit as st
from openai import AsyncOpenAI
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.bottom_container import bottom
from utils import style_page, clear_everything, meta_formatting, create_logger

title = "🤖 Ollama Chatbot Arena"
st.set_page_config(page_title=title, layout="wide")
style_page()
st.title(title)

with stylable_container(
    key="overview",
    css_styles="""
        button {
            background-color: #ffffff;
            color: black;
            border-radius: 10px;
        }
        hr {
        background-color: white;
        margin: 0.5em 0;
        }
        """,
):

    st.write("""Welcome to the Ollama Chatbot Arena!

This is an app that lets you do a blind comparison of Ollama models and vote for which ones answered the prompt better.

Make sure you've got [Ollama](https://ollama.com/) running on your machine, ideally with the `OLLAMA_MAX_LOADED_MODELS` environment variable set to a value higher than 1.

```
OLLAMA_MAX_LOADED_MODELS=4 ollama serve
```

***

Let's get started!
""")

    st.page_link("pages/1_Select_Models.py", label="Select Models 🔍", icon="1️⃣")
    st.page_link("pages/2_The_Arena.py", label="The Arena 🏟️", icon="2️⃣")
    st.page_link("pages/3_The_Leaderboard.py", label="The Leaderboard 🏆", icon="3️⃣")