# Import necessary libraries
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# Configure Streamlit page settings
st.set_page_config(page_title="Recommendation system", page_icon="🎮")

# Set the title of the Streamlit app
st.title('Game Recommendations for PS4')

# Display Markdown content with a link to another page for searching games
st.markdown("""In this page we recommend 10 games based on the game you select in the box. 
            If you are not sure about the game to use as a reference, you can search
            <a href='Search_Games' target='_self'>here</a>.""", unsafe_allow_html=True)

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

# Initialize a MultiLabelBinarizer for one-hot encoding genres
mlb = MultiLabelBinarizer(sparse_output=True)

# Combine Genre columns into a single column separated by semicolons
df_all['Genre'] = (df_all['Genre1'] + ';' + df_all['Genre2'] + ';' + df_all['Genre3']).astype(str)

# Remove trailing semicolons from the 'Genre' column
df_all['Genre'] = df_all['Genre'].apply(lambda x: x.rstrip(';'))

# Use MultiLabelBinarizer to one-hot encode genres
encoded_sparse_matrix = mlb.fit_transform(df_all['Genre'].str.split(";"))

# Calculate cosine similarity for each game based on genres
cosine_sim = cosine_similarity(encoded_sparse_matrix)

# Create a selectbox widget for selecting a game as a reference
selected_game = st.selectbox('Select one videogame used as a reference', 
                             df_all['Game'].sort_values(),
                             index=None,
                             placeholder="Type in or choose from the box")

# If no game is selected
if selected_game is not None:
    # Get the index of the selected game
    index_game = df_all.loc[(df_all['Game'] == selected_game)].index[0]

    # Calculate similarity percentages and add them to the DataFrame
    df_all['Similarity'] = round(pd.Series(cosine_sim[index_game]) * 100, 0).astype(int)

    # Display detailed information about the selected game
    st.markdown('''
                #### Selected videogame:
                ''')
    st.table(df_all.loc[[index_game], ['Rank', 'Game', 'Genre1', 'Genre2', 'Genre3', 'Score']])

    # Remove the selected game from the DataFrame for recommendation purposes
    df_all = df_all.drop(index=index_game, axis=0)

    # Sort the remaining games by similarity and score, and select the top 10
    df_all_top_10 = df_all.sort_values(by=['Similarity', 'Score'], ascending=[False, False])[:10]

    # Append '%' to the similarity scores for display
    df_all_top_10['Similarity'] = df_all_top_10['Similarity'].astype(str) + '%'

    # Display the top 10 recommended games
    st.markdown('''
                #### Top 10 recommendations!
                ''')
    st.table(df_all_top_10[['Rank', 'Game', 'Genre1', 'Genre2', 'Genre3', 'Score', 'Similarity']])