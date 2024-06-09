# Import necessary libraries
from datetime import datetime
import pandas as pd
import numpy as np
import streamlit as st

# Configure Streamlit page settings
st.set_page_config(page_title="Search Games", page_icon="🎮")

# Set the title of the Streamlit app
st.title('Search PS4 Games')

# Display Markdown content describing how to use the search filters
st.markdown("""In this page, you can find the game by genres (select up to 3), title, release year and score. 
            Apply filters in the sidebar (on the left side) to narrow the list down. The results will be displayed below.""")

# Set the header for the sidebar
st.sidebar.header("Apply filters")

# Define a custom function to format scores with one decimal place
def format_score(score):
    return '{:,.1f}'.format(score).replace('.', ',')

# Define a function to rename specific columns in a DataFrame
def rename_columns(df):
    dict_rename = {"genre1": "Genre1", "genre2": "Genre2", "genre3": "Genre3"}
    df = df.rename(columns=dict_rename)
    return df

# Load the games dataset
df_all = pd.read_csv('recommendation_games/games.csv')

# Fill empty values with empty string
df_all = df_all.fillna('')

# Rename columns to match the desired format
df_all = rename_columns(df_all)

# Apply the custom score formatting function to the 'Score' column
df_all['Score'] = df_all['Score'].apply(format_score)

# Get the unique genres and remove empty strings
unique_genres = (pd.concat([df_all['Genre1'], df_all['Genre2'], df_all['Genre3']])).unique()
unique_genres = unique_genres[unique_genres != '']

# Add a text input widget to the sidebar for searching games by title
st.sidebar.markdown("### Title")
keyword = st.sidebar.text_input('Input the word the game you are searching might contain:')
keyword_match = (df_all['Game'].str.lower().str.contains(keyword.lower()))

# Add a multiselect widget to the sidebar for selecting game genres
st.sidebar.markdown("### Genres")
unique_genres_sorted = np.sort(unique_genres[unique_genres != ''])
target_genres = st.sidebar.multiselect('Select Genres (up to 3)', options=list(unique_genres_sorted))

# Create an empty mask initially set to True for genre filtering
genre_match = np.ones(len(df_all), dtype=bool)

# Iterate over target genres and update the mask
for genre in target_genres:
    if genre is not None:
        # Check if any of the three columns contain the target genre
        bool_genre = np.any(df_all[['Genre1', 'Genre2', 'Genre3']].eq(genre), axis=1)
        # Update the mask by ANDing with the boolean array for the current genre
        genre_match &= bool_genre

# Add a slider widget to the sidebar for selecting the release year range
st.sidebar.markdown("### Release Year")
min_year = int(df_all['Release'].apply(lambda x: x[-4:]).min())
max_year = int(df_all['Release'].apply(lambda x: x[-4:]).max())
min_release_year, max_release_year = st.sidebar.slider(
    'Select the range',
    min_year, max_year, (min_year, max_year))

# Filter rows based on the selected release year range
release_year_match = (pd.to_datetime(df_all['Release'], format='%d/%m/%Y').dt.year >= min_release_year) & \
                     (pd.to_datetime(df_all['Release'], format='%d/%m/%Y').dt.year <= max_release_year)

# Add a slider widget to the sidebar for selecting the score range
st.sidebar.markdown("### Score")
scores = df_all['Score'].str.replace(',', '.').astype(float)
min_score = 6
max_score = 10
min_score_filter, max_score_filter = st.sidebar.slider(
    'Select the range',
    min_score, max_score,
    value=(min_score, max_score),
    step=1)

# Filter rows based on the selected score range
score_match = (scores >= min_score_filter) & (scores <= max_score_filter)

# Use the mask to filter the DataFrame based on the selected filters
filtered_genre_df = df_all[genre_match & keyword_match & release_year_match & score_match]

# Display the filtered DataFrame as a table in the app
st.table(filtered_genre_df)
