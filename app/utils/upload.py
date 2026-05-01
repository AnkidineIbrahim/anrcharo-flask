import os
import uuid
from PIL import Image
from flask import current_app

ALLOWED = {'jpg', 'jpeg', 'png', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

def save_image_local(file_storage, subfolder=''):
    """Save uploaded image locally, returns filename."""
    if not allowed_file(file_storage.filename):
        raise ValueError('Format de fichier non autorisé.')

    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    folder = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        folder = os.path.join(folder, subfolder)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)

    img = Image.open(file_storage)
    img = img.convert('RGB')

    # Max 1920px wide
    max_w = 1920
    if img.width > max_w:
        ratio = max_w / img.width
        img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)

    img.save(path, optimize=True, quality=88)
    return filename

def save_image_cloudinary(file_storage, folder='anrcharo'):
    """Upload to Cloudinary, returns (public_id, secure_url, thumb_url)."""
    import cloudinary.uploader
    result = cloudinary.uploader.upload(
        file_storage,
        folder=folder,
        transformation=[{'quality': 'auto', 'fetch_format': 'auto'}],
    )
    public_id  = result['public_id']
    secure_url = result['secure_url']
    thumb_url  = cloudinary.CloudinaryImage(public_id).build_url(
        width=600, height=400, crop='fill', quality='auto'
    )
    return public_id, secure_url, thumb_url

def delete_image_local(filename):
    try:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

def delete_image_cloudinary(public_id):
    try:
        import cloudinary.uploader
        cloudinary.uploader.destroy(public_id)
    except Exception:
        pass
