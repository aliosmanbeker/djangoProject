from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils.crypto import get_random_string
from .forms import RegistrationForm, LoginForm
from .models import MyUser

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.activation_code = get_random_string(length=32)  # Aktivasyon kodu oluştur
            user.save()
            send_activation_email(user)
            messages.success(request, 'Kayıt başarılı! Lütfen e-postanızı kontrol edin ve hesabınızı etkinleştirin.')
            return redirect('register')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def send_activation_email(user):
    activation_url = f"{settings.SITE_URL}/accounts/activate/{user.activation_code}/"
    subject = 'Hesabınızı Etkinleştirin'
    message = f"Hesabınızı etkinleştirmek için aşağıdaki bağlantıya tıklayın:\n\n{activation_url}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

def activate_account(request, code):
    try:
        user = MyUser.objects.get(activation_code=code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        login(request, user)
        messages.success(request, 'Hesabınız başarıyla etkinleştirildi!')
        return redirect('welcome')
    except MyUser.DoesNotExist:
        messages.error(request, 'Geçersiz aktivasyon kodu.')
        return redirect('home')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'Giriş başarılı! Hoş geldiniz.')
                    return redirect('welcome')
                else:
                    messages.error(request, 'Hesabınız henüz etkinleştirilmemiş. Lütfen e-postanızı kontrol edin.')
            else:
                messages.error(request, 'Geçersiz giriş bilgileri. Lütfen tekrar deneyin.')
        else:
            messages.error(request, 'Geçersiz giriş bilgileri. Lütfen tekrar deneyin.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def home(request):
    return render(request, 'accounts/home.html')

def welcome(request):
    return render(request, 'accounts/welcome.html')

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = MyUser.objects.get(email=email)
            user.reset_password_token = get_random_string(length=32)
            user.save()
            send_password_reset_email(user)
            messages.success(request, 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.')
            return redirect('password_reset')
        except MyUser.DoesNotExist:
            messages.error(request, 'Bu e-posta adresi sistemde kayıtlı değil.')
    return render(request, 'accounts/password_reset.html')

def send_password_reset_email(user):
    reset_url = f"{settings.SITE_URL}/accounts/password_reset_confirm/{user.reset_password_token}/"
    subject = 'Şifrenizi Sıfırlayın'
    message = f"Merhaba, {user.email}.\n\nŞifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:\n\n{reset_url}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

def password_reset_confirm(request, token):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = MyUser.objects.get(email=email, reset_password_token=token)
            user.set_password(password)
            user.reset_password_token = ''
            user.save()
            messages.success(request, 'Şifreniz başarıyla yenilendi.')
            return redirect('login')
        except MyUser.DoesNotExist:
            messages.error(request, 'Geçersiz e-posta adresi veya token.')
    return render(request, 'accounts/password_reset_confirm.html', {'token': token})
