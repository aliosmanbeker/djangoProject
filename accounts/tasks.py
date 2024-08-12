from __future__ import absolute_import, unicode_literals
from django.core.mail import send_mail
from .models import MyUser
from .utils import resize_and_save_images
from celery import shared_task
import zipfile
import os
from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .models import Post

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

@shared_task
def archive_post_and_notify(post_id, archiver_email):
    try:
        post = Post.objects.get(id=post_id)
        zip_filename = f"post_{post_id}.zip"
        zip_filepath = os.path.join(settings.MEDIA_ROOT, zip_filename)

        # Dosyaları zip olarak sıkıştırma
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for image in post.images.all():
                zipf.write(image.image.path, os.path.basename(image.image.path))
            zipf.writestr("text.txt", post.text)

        # Slack'e dosya yükleme ve mesaj gönderme
        upload_file_to_slack_v2(
            settings.SLACK_CHANNEL_ID,
            zip_filepath,
            f"{archiver_email} kullanıcısı {post.user.email} kullanıcısının bir postunu arşivledi."
        )

    except Post.DoesNotExist:
        return "Post bulunamadı"
    except Exception as e:
        return str(e)

def upload_file_to_slack_v2(channel_id, file_path, text):
    client = WebClient(token=settings.SLACK_API_TOKEN)
    try:
        response = client.files_upload_v2(
            channels=channel_id,
            file=file_path,
            initial_comment=text
        )
        if response["ok"]:
            print("File uploaded successfully")
        else:
            print(f"Failed to upload file: {response['error']}")
    except SlackApiError as e:
        print(f"Error uploading file: {e.response['error']}")
