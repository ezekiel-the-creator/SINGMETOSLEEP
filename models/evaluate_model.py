import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
import pickle

# Load test data
test_data = pd.read_csv('data/test_data.csv')

# Features and targets
X_test = test_data[['age', 'gender']]
y_genre_test = test_data['genre']
y_artist_test = test_data['artist']

# Load encoders
with open('data/le_genre.pkl', 'rb') as f:
    le_genre = pickle.load(f)
with open('data/le_artist.pkl', 'rb') as f:
    le_artist = pickle.load(f)

# Load models
with open('data/genre_classifier.pkl', 'rb') as f:
    genre_classifier = pickle.load(f)
with open('data/artist_classifier.pkl', 'rb') as f:
    artist_classifier = pickle.load(f)

# Predict on test data
genre_predictions = genre_classifier.predict(X_test)
artist_predictions = artist_classifier.predict(X_test)

# Decode predictions for readability
genre_predictions_decoded = le_genre.inverse_transform(genre_predictions)
artist_predictions_decoded = le_artist.inverse_transform(artist_predictions)
y_genre_test_decoded = le_genre.inverse_transform(y_genre_test)
y_artist_test_decoded = le_artist.inverse_transform(y_artist_test)

# Evaluate performance
genre_accuracy = accuracy_score(y_genre_test, genre_predictions)
artist_accuracy = accuracy_score(y_artist_test, artist_predictions)

print("Genre Classifier Accuracy:", genre_accuracy)
print("Genre Classification Report:\n", classification_report(y_genre_test_decoded, genre_predictions_decoded))
print("Artist Classifier Accuracy:", artist_accuracy)
print("Artist Classification Report:\n", classification_report(y_artist_test_decoded, artist_predictions_decoded))

# Test a sample prediction
sample_input = pd.DataFrame([[22, 1]], columns=['age', 'gender'])  # Example: 22-year-old male
sample_genre_pred = le_genre.inverse_transform(genre_classifier.predict(sample_input))[0]
sample_artist_pred = le_artist.inverse_transform(artist_classifier.predict(sample_input))[0]
print(f"Sample Prediction (Age 22, Male): Genre = {sample_genre_pred}, Artist = {sample_artist_pred}")