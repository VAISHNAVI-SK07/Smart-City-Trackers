import re
from difflib import SequenceMatcher
from models.complaint_model import find_nearby_complaints

# Combining multiple signals catches more real-world duplicates than any
# single method alone. Citizens paraphrase heavily ("Bridge wall broken"
# vs "Bridges broken"), so character-sequence matching alone often misses
# genuine duplicates. Word overlap catches shared key nouns even when
# phrasing, word order, or singular/plural forms differ.
SIMILARITY_THRESHOLD = 0.4

# Common words that don't help identify what the complaint is actually about.
STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'near', 'in', 'on', 'at',
    'of', 'to', 'and', 'has', 'have', 'not', 'this', 'that', 'it', 'for',
    'with', 'been', 'being', 'by', 'from', 'as'
}


def _text_similarity(a, b):
    """Character-sequence similarity ratio, 0.0 (different) to 1.0 (identical)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _normalize_word(word):
    """Very basic stemming: lowercase, strip punctuation, strip trailing 's'."""
    word = re.sub(r'[^a-z0-9]', '', word.lower())
    if len(word) > 3 and word.endswith('s'):
        word = word[:-1]
    return word


def _word_overlap_similarity(a, b):
    """
    Jaccard similarity between the meaningful words of two strings.
    Catches cases like "Bridge wall broken" vs "Bridges broken" - different
    structure and pluralization, but clearly about the same thing.
    """
    words_a = {_normalize_word(w) for w in a.split() if _normalize_word(w) and _normalize_word(w) not in STOPWORDS}
    words_b = {_normalize_word(w) for w in b.split() if _normalize_word(w) and _normalize_word(w) not in STOPWORDS}

    if not words_a or not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def _combined_similarity(a, b):
    """Takes the best signal from character-sequence and word-overlap matching."""
    return max(_text_similarity(a, b), _word_overlap_similarity(a, b))


def check_possible_duplicate(category, description, latitude, longitude,
                              exclude_id=None, title=None):
    """
    Looks for existing, still-open complaints in the same category and
    nearby location whose title OR description is similar to this one,
    using a combination of character-sequence and word-overlap matching.

    Returns a list of possible-duplicate matches (each with id, title, and
    similarity score) - never auto-deletes or auto-merges anything. The
    admin sees a warning and decides.
    """
    if latitude is None or longitude is None:
        return []

    nearby = find_nearby_complaints(category, latitude, longitude, exclude_id=exclude_id)

    matches = []
    for candidate in nearby:
        desc_similarity = _combined_similarity(description, candidate['description'])
        title_similarity = 0.0
        if title and candidate.get('title'):
            title_similarity = _combined_similarity(title, candidate['title'])

        best_similarity = max(desc_similarity, title_similarity)

        if best_similarity >= SIMILARITY_THRESHOLD:
            matches.append({
                'complaint_id': candidate['id'],
                'title': candidate['title'],
                'similarity': round(best_similarity, 2)
            })

    matches.sort(key=lambda m: m['similarity'], reverse=True)
    return matches
