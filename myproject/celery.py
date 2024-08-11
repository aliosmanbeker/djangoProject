from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django'nun varsayılan ayarlarını Celery'e yüklemek için
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# Django ayarlarını Celery'e aktarıyoruz
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tüm uygulamalardaki görevleri otomatik keşfet
app.autodiscover_tasks()
