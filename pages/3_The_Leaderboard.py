import streamlit as st
import ollama
import jsonlines
import pandas as pd

from streamlit_extras.stylable_container import stylable_container
from trueskill import Rating, rate_1vs1
from utils import all_chat_models, style_page

title = "🏆 The Leaderboard"
st.set_page_config(page_title=title, layout="wide")
style_page()
st.title(title)

st.write("The models are ranked using Microsoft's TrueSkill algorithm.")

models = all_chat_models()

models_with_ratings = {
  name: {
    "size": size,
    "rating": Rating(), 
    "comparisons": 0
  } 
  for name, size in models
}

with jsonlines.open('logs/voting.log') as reader:
    for row in reader:
      if row["model1"] in models_with_ratings and row["model2"] in models_with_ratings:
        m1 = models_with_ratings[row["model1"]]["rating"]
        m2 = models_with_ratings[row["model2"]]["rating"]

        if row["choice"] == "same":
          m1, m2 = rate_1vs1(m1, m2, drawn=True)
        if row["choice"] == "model1":
          m1, m2 = rate_1vs1(m1, m2)
        if row["choice"] == "model2":
          m2, m1 = rate_1vs1(m2, m1)
        
        models_with_ratings[row["model1"]]["rating"] = m1
        models_with_ratings[row["model1"]]["comparisons"] += 1

        models_with_ratings[row["model2"]]["rating"] = m2
        models_with_ratings[row["model2"]]["comparisons"] += 1

df = pd.DataFrame({
    "Name": models_with_ratings.keys(),
    "Size": [v['size'] for k,v in models_with_ratings.items()],
    "Rating": [v['rating'].mu for k,v in models_with_ratings.items()],
    "Certainty": [v['rating'].sigma for k,v in models_with_ratings.items()],
    "Comparisons": [v['comparisons'] for k,v in models_with_ratings.items()]
  })

st.dataframe(
  df.sort_values(by = ["Rating"], ascending=False), hide_index=True
)