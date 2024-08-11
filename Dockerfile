# Python tabanlı bir Docker imajı seçin
FROM python:3.10-slim

# Çalışma dizinini oluşturun
WORKDIR /usr/src/app

# Gerekli paketleri yükleyin (Debian/Ubuntu tabanlı bir Docker imajı kullanıyorsanız)
RUN apt-get update && apt-get install -y gcc build-essential

# Gereksinimlerinizi yükleyin
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamanın tüm dosyalarını kopyalayın
COPY . .

# Django ayarlarını belirleyin
ENV DJANGO_SETTINGS_MODULE=myproject.settings

# Celery için ortam değişkenlerini belirleyin
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0

# Django statik dosyaları toplayın
RUN python manage.py collectstatic --noinput

# Django sunucusunu ve Celery'i başlatın
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi"]
