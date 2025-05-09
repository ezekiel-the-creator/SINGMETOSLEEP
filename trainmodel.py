import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load training data
train_data = pd.read_csv('data/train_data.csv')

# Features and targets
X_train = train_data[['age', 'gender']]
y_genre_train = train_data['genre']
y_artist_train = train_data['artist']

# Train genre classifier
genre_classifier = RandomForestClassifier(random_state=42)
genre_classifier.fit(X_train, y_genre_train)

# Train artist classifier
artist_classifier = RandomForestClassifier(random_state=42)
artist_classifier.fit(X_train, y_artist_train)

# Save models
with open('data/genre_classifier.pkl', 'wb') as f:
    pickle.dump(genre_classifier, f)
with open('data/artist_classifier.pkl', 'wb') as f:
    pickle.dump(artist_classifier, f)

print("Models trained and saved successfully!")