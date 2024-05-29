import streamlit as st
import pickle
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_KEY = 'c7ec19ffdd3279641fb606d19ceb9bb1'
BASE_URL = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500/"
PLACEHOLDER_POSTER_URL = "https://via.placeholder.com/500x750.png?text=No+Poster+Available"

# Setting up retries
session = requests.Session()
retry = Retry(
    total=5,  # Number of retries
    backoff_factor=1,  # Increased backoff factor for more delay between retries
    status_forcelist=[500, 502, 503, 504],  # Retry on these HTTP status codes
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def fetch_poster(movie_id):
    url = BASE_URL.format(movie_id, API_KEY)
    try:
        response = session.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return POSTER_BASE_URL + poster_path
        else:
            return PLACEHOLDER_POSTER_URL
    except requests.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return PLACEHOLDER_POSTER_URL

@st.cache_data
def load_data():
    with open("movies.pkl", 'rb') as f:
        movies = pickle.load(f)
    with open("similarity.pkl", 'rb') as f:
        similarity = pickle.load(f)
    movies_list = movies['title'].values
    return movies, similarity, movies_list

movies, similarity, movies_list = load_data()

st.header("Get Movie Recommendation")

# Create a dropdown to select a movie
selected_movie = st.selectbox("Select a movie:", movies_list)

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommended_movies = []
    recommended_posters = []
    for i in distances[1:11]:  # Get top 10 recommendations
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters

# Adding custom CSS for text styling
st.markdown("""
    <style>
    .movie-title {
        font-family: 'Arial', sans-serif;
        word-wrap: break-word;
        font-size: 16px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

if st.button("Recommend"):
    movie_names, movie_posters = recommend(selected_movie)
    # Display recommendations in 2 rows of 5 columns each
    for i in range(0, 10, 5):
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if i + idx < len(movie_names):
                with col:
                    st.image(movie_posters[i + idx])
                    st.markdown(f"<div class='movie-title'>{movie_names[i + idx]}</div>", unsafe_allow_html=True)
