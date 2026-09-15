import os
import uuid
from werkzeug.utils import secure_filename
from config import Config


def is_allowed_image(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_IMAGE_EXTENSIONS


def save_uploaded_image(file_storage):
    """
    Validates and saves an uploaded image file.
    Returns the relative path to store in the database, or None if no file
    was provided. Raises ValueError if the file type isn't allowed.

    File size is already capped globally by Config.MAX_CONTENT_LENGTH
    (Flask rejects oversized requests before this code even runs).
    """
    if not file_storage or file_storage.filename == '':
        return None

    if not is_allowed_image(file_storage.filename):
        raise ValueError(
            f"Invalid image type. Allowed types: {', '.join(Config.ALLOWED_IMAGE_EXTENSIONS)}"
        )

    original_name = secure_filename(file_storage.filename)
    ext = original_name.rsplit('.', 1)[1].lower()
    # Random unique filename prevents overwriting existing files and
    # avoids leaking any information from the original filename.
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = Config.UPLOAD_FOLDER
    os.makedirs(upload_dir, exist_ok=True)

    full_path = os.path.join(upload_dir, unique_name)
    file_storage.save(full_path)

    # Store the path using forward slashes so it's consistent whether the
    # app runs on Windows or Linux, and easy to use as a URL path later.
    return f"{upload_dir}/{unique_name}".replace('\\', '/')
