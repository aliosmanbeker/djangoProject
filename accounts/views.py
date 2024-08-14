from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.utils.crypto import get_random_string
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .forms import RegistrationForm, LoginForm, UploadForm, ImageForm, ProfileUpdateForm
from .models import MyUser, Post, Image, Follow
from django.contrib.auth import get_user_model
from .tasks import archive_post_and_notify
from .serializers import UserSerializer, PostSerializer
from django.core.cache import cache


# Django Views
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_activation_email.delay(user.id)  # Asenkron e-posta gönderimi
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
            user = authenticate(request, username=form.cleaned_data.get('username'),
                                password=form.cleaned_data.get('password'))
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


@login_required
def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST)
        image_form = ImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            image = image_form.save(commit=False)
            image.post = post
            image.save()

            return redirect('post_detail', post_id=post.id)
    else:
        form = UploadForm()
        image_form = ImageForm()
    return render(request, 'accounts/upload.html', {'form': form, 'image_form': image_form})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'accounts/post_detail.html', {'post': post})


User = get_user_model()


@login_required
def user_list(request):
    users = MyUser.objects.exclude(id=request.user.id)
    following_ids = request.user.following.values_list('id', flat=True)
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'following_ids': following_ids,
    })


@login_required
def follow_unfollow(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)
    follow_record, created = Follow.objects.get_or_create(follower=request.user, followed=user)
    if not created:
        follow_record.delete()
    return redirect('user_list')


@login_required
def followed_posts(request):
    followed_users = MyUser.objects.filter(followers__follower=request.user)
    posts = Post.objects.filter(user__in=followed_users)
    return render(request, 'accounts/followed_posts.html', {'posts': posts})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Cache'i temizle
            cache_key = f"profile_{request.user.id}"
            cache.delete(cache_key)
            messages.success(request, 'Profiliniz başarıyla güncellendi.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {'form': form, 'posts': posts})


def archive_post(request, post_id):
    if request.method == 'POST':
        archive_post_and_notify.delay(post_id, request.user.email)
        return redirect('followed_posts')


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


# Profil View'u (Cache ile)
@login_required
def profile_view(request, user_id):
    # Cache anahtarını belirliyoruz
    cache_key = f"profile_{user_id}"

    # Cache'te bu anahtar var mı diye kontrol ediyoruz
    user_profile = cache.get(cache_key)

    if not user_profile:
        # Eğer cache'te yoksa, veriyi veri tabanından çekiyoruz
        user_profile = get_object_or_404(MyUser, id=user_id)

        # Cache'e bu veriyi ekliyoruz ve TTL süresini ayarlıyoruz
        cache.set(cache_key, user_profile, timeout=settings.CACHE_TTL)

    # Veriyi döndürüyoruz
    return render(request, 'accounts/profile.html', {'user': user_profile})


# REST API Views
class UserList(generics.ListCreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
