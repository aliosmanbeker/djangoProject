from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from PIL import Image
import os
from .models import MyUser
from .utils import resize_and_save_images

@shared_task
def send_activation_email(user_id):
    user = MyUser.objects.get(id=user_id)
    activation_url = f"{settings.SITE_URL}/accounts/activate/{user.activation_code}/"
    subject = 'Hesabınızı Etkinleştirin'
    message = f"Hesabınızı etkinleştirmek için aşağıdaki bağlantıya tıklayın:\n\n{activation_url}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

@shared_task
def resize_image(image_path):
    resize_and_save_images(image_path)
