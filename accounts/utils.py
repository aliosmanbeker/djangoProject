from PIL import Image as PilImage
import os
from django.conf import settings


def resize_and_save_images(image_instance):
    sizes = [(120, 120), (400, 400), (800, 800)]
    image_path = os.path.join(settings.MEDIA_ROOT, image_instance.image.name)

    resized_images = {}

    for size in sizes:
        resized_image = PilImage.open(image_path)
        resized_image.thumbnail(size, PilImage.LANCZOS)
        new_image_name = f"{size[0]}x{size[1]}_{image_instance.image.name}"
        path = os.path.join(settings.MEDIA_ROOT, 'uploads/resized', new_image_name)

        # Eğer dizin yoksa oluşturun
        os.makedirs(os.path.dirname(path), exist_ok=True)

        resized_image.save(path)

        # Boyutlandırılmış resim yolunu sakla
        resized_images[size] = f"uploads/resized/{new_image_name}"

    # Resim yollarını image_instance objesine ekle ve kaydet
    image_instance.image_120x120 = resized_images[(120, 120)]
    image_instance.image_400x400 = resized_images[(400, 400)]
    image_instance.image_800x800 = resized_images[(800, 800)]
    image_instance.save()