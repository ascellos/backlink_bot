from Levenshtein import ratio

def check_content_similarity(new_article: str, previous_articles: list):
    """
    Compares a new article against a list of previous articles.
    Returns the highest similarity score found (0.0 to 1.0) and which one it matched.
    """
    highest_similarity = 0.0
    most_similar_index = None

    for i, old_article in enumerate(previous_articles):
        similarity = ratio(new_article, old_article)
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar_index = i

    is_duplicate = highest_similarity >= 0.75  # 75% similar or more = flagged

    return {
        "highest_similarity": round(highest_similarity, 3),
        "is_duplicate": is_duplicate,
        "matched_index": most_similar_index
    }