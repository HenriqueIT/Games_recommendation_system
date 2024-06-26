from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# Title and description of the web application
st.write("# Welcome to Game Recommendation system! 👋")

st.markdown(
    """
    The main purpose of this web application is to **suggest videogames** on PS4 based on their **genres** and **scores**.
    """)

# Explanation of the main features of the application
st.markdown(
    """
    ### 2 Features
    - Recommend Games
    """)
with st.expander("See explanation"):
    st.write("""
        You can select one video game, and this application will suggest 10 video games with similar genres and the highest scores.
    """)

st.markdown(
    """
    - Search Games 
    """
)
with st.expander("See explanation"):
    st.write("""
        You can search videogames based on their title, release date and genres.
    """)