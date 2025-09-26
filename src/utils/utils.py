
from io import BytesIO
from PIL import Image
import os

from config.settings import DATA_DIR
UPLOADS_DIR = DATA_DIR / "uploads"


def save_image_with_max_size(image_data, filename, max_size_kb=500, max_pixels=(800, 800)):
    image = Image.open(BytesIO(image_data))
    image.thumbnail(max_pixels, Image.Resampling.LANCZOS)

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    save_path = f"{UPLOADS_DIR}/{filename}"
    quality = 95

    while True:
        image.convert("RGB").save(
            save_path,
            "JPEG",
            quality=quality,
            optimize=True
        )
        file_size = os.path.getsize(save_path) / 1024  # en Ko
        if file_size <= max_size_kb or quality <= 10:
            break
        quality -= 5

    return save_path