import pandas as pd
import pickle
from googleapiclient.discovery import build

# Load encoders and models
with open('data/le_gender.pkl', 'rb') as f:
    le_gender = pickle.load(f)
with open('data/le_genre.pkl', 'rb') as f:
    le_genre = pickle.load(f)
with open('data/le_artist.pkl', 'rb') as f:
    le_artist = pickle.load(f)
with open('data/genre_classifier.pkl', 'rb') as f:
    genre_classifier = pickle.load(f)
with open('data/artist_classifier.pkl', 'rb') as f:
    artist_classifier = pickle.load(f)

# YouTube API setup
YOUTUBE_API_KEY = 'AIzaSyC4-Q-6QJDesEJvfC0OW8xewKyU8bWr_j4'  # Replace with your API key
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Get user input
age = int(input("Enter age: "))
gender = input("Enter gender (Male/Female): ").capitalize()
gender_encoded = le_gender.transform([gender])[0]

# Predict genre and artist
sample_input = pd.DataFrame([[age, gender_encoded]], columns=['age', 'gender'])
genre_pred = le_genre.inverse_transform(genre_classifier.predict(sample_input))[0]
artist_pred = le_artist.inverse_transform(artist_classifier.predict(sample_input))[0]

# Search YouTube for artist video
search_response = youtube.search().list(
    q=f"{artist_pred} official music video",
    part='id,snippet',
    maxResults=1,
    type='video'
).execute()

video_id = search_response['items'][0]['id']['videoId']
video_title = search_response['items'][0]['snippet']['title']
video_url = f"https://www.youtube.com/watch?v={video_id}"

# Display recommendation
print(f"Recommended Genre: {genre_pred}")
print(f"Recommended Artist: {artist_pred}")
print(f"Watch: {video_title} - {video_url}")