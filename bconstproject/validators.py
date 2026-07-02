MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


def validate_uploaded_image(file):
    """Returns an Arabic error message if the uploaded image is invalid, else None."""
    if file.size > MAX_UPLOAD_SIZE:
        return 'حجم الصورة يجب ألا يتجاوز 5 ميجابايت'
    content_type = getattr(file, 'content_type', '') or ''
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        return 'صيغة الملف غير مدعومة، الرجاء رفع صورة (JPEG أو PNG أو WEBP أو GIF)'
    return None


def validate_uploaded_file(file, max_size=MAX_UPLOAD_SIZE):
    """Returns an Arabic error message if the uploaded file is too large, else None."""
    if file.size > max_size:
        return 'حجم الملف يجب ألا يتجاوز 5 ميجابايت'
    return None
