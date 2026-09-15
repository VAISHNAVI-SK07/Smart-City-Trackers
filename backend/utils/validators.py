import re

EMAIL_PATTERN = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def is_valid_email(email):
    return bool(email) and bool(EMAIL_PATTERN.match(email))


def is_valid_password(password):
    # Kept simple on purpose for a student demo project: 6+ characters.
    return isinstance(password, str) and len(password) >= 6


def is_non_empty_string(value, min_length=1, max_length=None):
    if not isinstance(value, str):
        return False
    value = value.strip()
    if len(value) < min_length:
        return False
    if max_length is not None and len(value) > max_length:
        return False
    return True


def is_valid_coordinate(lat, lng):
    try:
        lat = float(lat)
        lng = float(lng)
        return -90 <= lat <= 90 and -180 <= lng <= 180
    except (TypeError, ValueError):
        return False
