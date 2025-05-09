import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle

# Load dataset
df = pd.read_csv('data/music_data.csv')

# Encode categorical variables
le_gender = LabelEncoder()
le_genre = LabelEncoder()
le_artist = LabelEncoder()

df['gender'] = le_gender.fit_transform(df['gender'])
df['genre'] = le_genre.fit_transform(df['genre'])
df['artist'] = le_artist.fit_transform(df['artist'])

# Save encoders for later use
with open('data/le_gender.pkl', 'wb') as f:
    pickle.dump(le_gender, f)
with open('data/le_genre.pkl', 'wb') as f:
    pickle.dump(le_genre, f)
with open('data/le_artist.pkl', 'wb') as f:
    pickle.dump(le_artist, f)

# Define features and target
X = df[['age', 'gender']]
y_genre = df['genre']
y_artist = df['artist']

# Split data into training and testing sets
X_train, X_test, y_genre_train, y_genre_test = train_test_split(X, y_genre, test_size=0.2, random_state=42)
_, _, y_artist_train, y_artist_test = train_test_split(X, y_artist, test_size=0.2, random_state=42)

# Save processed data
pd.concat([X_train, y_genre_train, y_artist_train], axis=1).to_csv('data/train_data.csv', index=False)
pd.concat([X_test, y_genre_test, y_artist_test], axis=1).to_csv('data/test_data.csv', index=False)

print("Dataset preprocessed and saved successfully!")