import streamlit as st
import ollama
from streamlit_extras.stylable_container import stylable_container
from utils import all_chat_models, style_page

def update_selected_models():
  st.session_state.models = st.session_state.select_models
  st.session_state.selected_models = []


title = "🔍 Select the models"
st.set_page_config(page_title=title, layout="wide")
style_page()
st.title(title)
st.write("Below are a list of the models available on your machine. Choose at least two.")

if not "models" in st.session_state:
  st.session_state.models = []

if "select_models" not in st.session_state:
    st.session_state.select_models = st.session_state.models    


models = [name for name, size in all_chat_models()]

options = st.multiselect(
    "Choose models",
    models,
    key="select_models",
    on_change=update_selected_models
)

if len(options) > 0:
  st.session_state.models = options

  with stylable_container(
      key="next_round_button",
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
    if len(options) == 1:
      st.write("""***""")
      st.write("One model selected. Select one more.")
      st.stop()
    else:
        st.write(f"""***  
{len(options)} Models selected - It's time to enter the arena! 👇""")
        if st.button("Enter the Chatbot Arena"):
          st.switch_page("pages/2_The_Arena.py")