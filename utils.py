import time
import logging
import json
import streamlit as st

def style_page():
  st.html("""
  <style>
  hr {
      margin: -0.5em 0 0 0;
      background-color: red;
  }
  p.prompt {
      margin: 0;
      font-size: 14px;
  }

  img.spinner {
      margin: 0 0 0 0;
  }
  </style>
  """)


def clear_everything():
  st.session_state.messages1 = []
  st.session_state.messages2 = []
  del st.session_state.selected_models
  if "vote" in st.session_state:
      del st.session_state.vote

def meta_formatting(color, prefix, model_name):
    return f"## :{color}[{prefix}: {model_name}]"
