from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = False  # Kullanıcı başlangıçta aktif değil
        user.activation_code = get_random_string(length=32)  # Aktivasyon kodu oluştur
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.is_active = True  # Superuser başlangıçta aktif
        user.save(using=self._db)
        return user

class MyUser(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=32, blank=True)
    reset_password_token = models.CharField(max_length=32, blank=True)  # Şifre sıfırlama token'ı için alan

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
