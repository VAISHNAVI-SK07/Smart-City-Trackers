# Keyword -> category mapping. This is intentionally simple and transparent
# (not a black-box ML model) so it's easy to explain in a viva and easy to
# extend later. The admin can always override the suggestion.

CATEGORY_KEYWORDS = {
    'Road': ['pothole', 'road', 'street damage', 'crack', 'tar', 'asphalt', 'speed breaker'],
    'Waste': ['garbage', 'trash', 'waste', 'litter', 'dump', 'bin overflow'],
    'Drainage': ['drainage', 'drain', 'sewage', 'waterlog', 'stagnant water', 'blocked drain'],
    'Water': ['water leak', 'pipeline', 'water supply', 'tap', 'leakage', 'burst pipe'],
    'Streetlight': ['streetlight', 'street light', 'lamp post', 'light not working', 'dark street'],
    'Sanitation': ['sanitation', 'toilet', 'public restroom', 'hygiene', 'dirty', 'overflowing bin'],
    'Infrastructure': ['footpath', 'bridge', 'building', 'wall', 'infrastructure', 'public property'],
}


def suggest_category(title, description):
    """
    Scans title + description for keywords and returns the best-matching
    category, or 'Other' if nothing matches. This is a SUGGESTION only —
    the citizen picks the category on the form, and the admin can change it.
    """
    text = f"{title} {description}".lower()

    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score

    if not scores:
        return 'Other'

    return max(scores, key=scores.get)
