# Rule-based priority recommendation, as specified in Phase 1.
# Configurable: change these dicts/rules to tune behavior without
# touching any route or model code.

# Categories that are inherently more dangerous get a priority "floor" —
# they can never be recommended lower than this, regardless of severity.
CATEGORY_PRIORITY_FLOOR = {
    'Drainage': 'High',
    'Water': 'Medium',
    'Road': 'Medium',
}

SEVERITY_TO_PRIORITY = {
    'Critical': 'Critical',
    'High': 'High',
    'Medium': 'Medium',
    'Low': 'Low',
}

PRIORITY_RANK = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}


def recommend_priority(category, severity):
    """
    Combines the citizen-reported severity with a category-based floor.
    Example: a "Low" severity Drainage complaint still gets recommended
    as at least "High", since blocked drainage is a public health risk
    regardless of how the citizen rated it.

    Admin can always override this in the UI.
    """
    base = SEVERITY_TO_PRIORITY.get(severity, 'Medium')
    floor = CATEGORY_PRIORITY_FLOOR.get(category)

    if floor and PRIORITY_RANK[floor] > PRIORITY_RANK[base]:
        return floor
    return base
