import streamlit as st
import pickle
import pandas as pd
import requests

st.markdown(
    """
    <style>
    .title {
        color: #FF6347;
        font-size: 40px;
        text-align: center;
    }
    .subheader {
        color: #4B0082;
        font-size: 24px;
        text-align: center;
    }
    .recommendation {
        text-align: center;
        margin: 20px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=1cb0b32cfd452f5209c3401497a78c5f&language=en-US".format(movie_id)
    data = requests.get(url).json()
    if 'poster_path' in data:
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Image+Available"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommend_movies = []
    recommended_movie_posters = []

    for mov in movie_list:
        movie_id = movies.iloc[mov[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommend_movies.append(movies.iloc[mov[0]].title)

    return recommend_movies, recommended_movie_posters

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('🎬 Movie Recommender System')
st.markdown('<div class="title">Hope You enjoy these Recommendations </div>', unsafe_allow_html=True)

select_movies = st.selectbox(
    "Select a movie to get recommendations",
    movies['title'].values
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(select_movies)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.markdown(f'<div class="recommendation"><h3>{recommended_movie_names[i]}</h3></div>', unsafe_allow_html=True)
            st.image(recommended_movie_posters[i], use_column_width=True)


st.write("""
    <style>
    .stApp {
        background-color: #f0f0f0;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)