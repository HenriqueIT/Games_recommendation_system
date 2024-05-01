from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

st.set_page_config(page_title="Recommendation system", page_icon="🎮")

st.title('Game Recommendations for PS4')

st.markdown("""In this page we recommend 10 games based on the game you select in the box. 
            If you are not sure about the game to use as a reference, you can search
            <a href='Search_Games' target='_self'>here</a>.""", unsafe_allow_html=True)

# Define a custom formatting function
def format_score(score):
    return '{:,.1f}'.format(score).replace('.', ',')

def rename_columns(df):
    dict_rename = {"genre1": "Genre1", "genre2": "Genre2", "genre3": "Genre3"}
    df = df.rename(columns = dict_rename)
    return df

#df_all = pd.read_csv('games.csv')
df_all = pd.read_csv('recommendation_games/games.csv')

# Fill empty values with emoty string
df_all = df_all.fillna('')

# Rename columns
df_all = rename_columns(df_all)

# Format Score column
df_all['Score'] = df_all['Score'].apply(format_score)

mlb = MultiLabelBinarizer(sparse_output = True)

df_all['Genre'] = (df_all['Genre1'] + ';' + df_all['Genre2'] + ';' + df_all['Genre3']).astype(str)

# Remove all character ';' on the right side of the string
df_all['Genre'] = df_all['Genre'].apply(lambda x : x.rstrip(';'))

# Use MultilabelBinarizer to one hot encode categories
encoded_sparse_matrix = mlb.fit_transform(df_all['Genre'].str.split(";"))

# Use cosine_similarity to calculate the cosine similarity for each videgame
cosine_sim = cosine_similarity(encoded_sparse_matrix) #applying cosine similarity to tfidf_matrix

selected_game = st.selectbox('Select one videogame used as a reference', 
                             df_all['Game'].sort_values(),
                             index=None,
                             placeholder="Type in or choose from the box")

if selected_game is not None:

    index_game = df_all.loc[(df_all['Game'] == selected_game)].index[0]

    df_all['Similarity'] = round(pd.Series(cosine_sim[index_game])*100, 0).astype(int)

    #st.subheader('Detailed info on selected videogame')
    st.markdown('''
                #### Selected videogame:
                ''')
    st.table(df_all.loc[[index_game], ['Rank','Game','Genre1', 'Genre2', 'Genre3', 'Score']])

    df_all = df_all.drop(index = index_game, axis = 0)
    df_all_top_10 = df_all.sort_values(by=['Similarity', 'Score'], ascending=[False, False])[:10]

    df_all_top_10['Similarity'] = df_all_top_10['Similarity'].astype(str) + '%'

    st.markdown('''
                #### Top 10 recommendations!
                ''')

    st.table(df_all_top_10[['Rank','Game','Genre1', 'Genre2', 'Genre3', 'Score', 'Similarity']])