# recommender.py
def recommend_music(age, gender):
    # Simple rule-based recommender for testing
    if age < 20:
        genre = "HipHop"
        artist = "Drake"
        youtube = "https://www.youtube.com/@DrakeOfficial"
    elif age < 30:
        genre = "Pop"
        artist = "Taylor Swift"
        youtube = "https://www.youtube.com/@TaylorSwift"
    else:
        genre = "Rock"
        artist = "Imagine Dragons"
        youtube = "https://www.youtube.com/@ImagineDragons"
    return {"genre": genre, "artist": artist, "youtube": youtube}

# Test the recommender
if __name__ == "__main__":
    test_cases = [(22, 1), (25, 0), (35, 1)]  # (age, gender: 1=Male, 0=Female)
    for age, gender in test_cases:
        result = recommend_music(age, gender)
        print(f"Age: {age}, Gender: {'Male' if gender == 1 else 'Female'}")
        print(f"Recommended Genre: {result['genre']}, Artist: {result['artist']}, YouTube: {result['youtube']}\n")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          