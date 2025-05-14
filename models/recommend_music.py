import pandas as pd
import pickle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import random
import time
import logging
import pickle as pk
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OAuth setup
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRETS_FILE = os.path.expanduser('~/Documents/CS/MusicRecommender/client_secrets.json')
CREDENTIALS_FILE = os.path.expanduser('~/Documents/CS/MusicRecommender/token.pkl')

def get_youtube_client():
    credentials = None
    if os.path.exists(CREDENTIALS_FILE):
        logger.info("Loading credentials from token.pkl")
        with open(CREDENTIALS_FILE, 'rb') as token:
            credentials = pk.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            logger.info("Refreshing expired credentials")
            credentials.refresh(Request())
        else:
            logger.info("Running OAuth flow")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open(CREDENTIALS_FILE, 'wb') as token:
            logger.info("Saving credentials to token.pkl")
            pk.dump(credentials, token)
    # Configure retries for API client
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return build('youtube', 'v3', credentials=credentials, cache_discovery=False)

youtube = get_youtube_client()

# Load encoders and models
DATA_DIR = os.path.expanduser('~/Documents/CS/MusicRecommender/data')
try:
    with open(os.path.join(DATA_DIR, 'le_gender.pkl'), 'rb') as f:
        le_gender = pickle.load(f)
    with open(os.path.join(DATA_DIR, 'le_genre.pkl'), 'rb') as f:
        le_genre = pickle.load(f)
    with open(os.path.join(DATA_DIR, 'le_artist.pkl'), 'rb') as f:
        le_artist = pickle.load(f)
    with open(os.path.join(DATA_DIR, 'genre_classifier.pkl'), 'rb') as f:
        genre_classifier = pickle.load(f)
    with open(os.path.join(DATA_DIR, 'artist_classifier.pkl'), 'rb') as f:
        artist_classifier = pickle.load(f)
except FileNotFoundError:
    logger.error("Model/encoder files missing in ~/Documents/CS/MusicRecommender/data/")
    raise

def recommend_music(age, gender, used_artists=None, used_videos=None):
    if used_artists is None:
        used_artists = set()
    if used_videos is None:
        used_videos = set()
    try:
        logger.info(f"Recommending for age {age}, gender {gender}")
        gender_encoded = le_gender.transform([gender.capitalize()])[0]
        sample_input = pd.DataFrame([[age + random.uniform(-0.5, 0.5), gender_encoded]], columns=['age', 'gender'])
        genre_pred = le_genre.inverse_transform(genre_classifier.predict(sample_input))[0]
        artist_probs = artist_classifier.predict_proba(sample_input)[0]
        artist_indices = list(range(len(artist_probs)))
        artist_options = [
            idx for idx, _ in sorted(
                zip(artist_indices, artist_probs), key=lambda x: x[1], reverse=True
            ) if le_artist.inverse_transform([idx])[0] not in used_artists
        ]
        if not artist_options:
            logger.warning("No new artists available, using any artist")
            artist_options = artist_indices
        artist_idx = random.choice(artist_options[:5])
        artist_pred = le_artist.inverse_transform([artist_idx])[0]
        used_artists.add(artist_pred)
        logger.info(f"Predicted genre: {genre_pred}, artist: {artist_pred}")
        search_terms = [f"{artist_pred} music", f"{artist_pred} {genre_pred.lower()}"]
        random.shuffle(search_terms)
        video_id = None
        video_title = None
        for query in search_terms:
            try:
                logger.info(f"Searching YouTube for: {query}")
                search_response = youtube.search().list(
                    q=query,
                    part='id,snippet',
                    maxResults=3,  # Reduced to save quota
                    type='video'
                ).execute()
                if search_response['items']:
                    for item in search_response['items']:
                        candidate_video_id = item['id']['videoId']
                        if candidate_video_id not in used_videos:
                            video_id = candidate_video_id
                            video_title = item['snippet']['title']
                            used_videos.add(video_id)
                            logger.info(f"Selected video: {video_title} ({video_id})")
                            break
                if video_id:
                    break
            except HttpError as e:
                logger.error(f"Search error for query {query}: {e}")
        if not video_id:
            logger.warning(f"No unique videos found for {artist_pred}")
            return None, f"No unique videos found for {artist_pred}."
        return video_id, f"Age {age}: {genre_pred} - {artist_pred} - {video_title} (https://www.youtube.com/watch?v={video_id})"
    except HttpError as e:
        logger.error(f"YouTube API error: {e}")
        return None, f"YouTube API error: {e}"
    except ValueError as e:
        logger.error(f"Input error: {e}")
        return None, f"Input error: {e}"

def create_youtube_playlist(title, video_ids):
    try:
        logger.info(f"Creating playlist: {title}")
        playlist_response = youtube.playlists().insert(
            part='snippet,status',
            body={
                'snippet': {
                    'title': title,
                    'description': 'Sleep playlist generated by Music Recommender'
                },
                'status': {'privacyStatus': 'private'}
            }
        ).execute()
        playlist_id = playlist_response['id']
        for video_id in video_ids:
            logger.info(f"Adding video {video_id} to playlist {playlist_id}")
            youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            ).execute()
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        logger.info(f"Playlist created: {playlist_url}")
        return playlist_url
    except HttpError as e:
        logger.error(f"Error creating playlist: {e}")
        return f"Error creating playlist: {e}"

def get_sleep_playlist(age, gender):
    video_ids = []
    recommendations = []
    used_artists = set()
    used_videos = set()
    for a in range(age, max(age - 7, 15), -1):
        for attempt in range(2):  # Retry once
            video_id, result = recommend_music(a, gender, used_artists, used_videos)
            if video_id:
                video_ids.append(video_id)
                recommendations.append(result)
                break
            logger.warning(f"Retry {attempt+1} for age {a}")
            time.sleep(3)
        time.sleep(3)  # Increased to avoid rate limits
    if video_ids:
        playlist_title = f"Sleep Vibes for Age {age} - {time.strftime('%Y-%m-%d')}"
        playlist_url = create_youtube_playlist(playlist_title, video_ids)
        if not isinstance(playlist_url, str) or "Error" in playlist_url:
            logger.error(f"Failed to create playlist: {playlist_url}")
            return recommendations, "Failed to create playlist."
        return recommendations, playlist_url
    logger.warning("No videos found for sleep playlist")
    return [], "No videos found for sleep playlist."