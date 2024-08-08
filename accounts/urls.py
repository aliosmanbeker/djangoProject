from django.urls import path
from . import views
from .views import register, login_view, home, welcome, activate_account, password_reset, password_reset_confirm, upload_view , post_detail, user_list, follow_unfollow,followed_posts, profile

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', home, name='home'),
    path('welcome/', welcome, name='welcome'),
    path('activate/<str:code>/', activate_account, name='activate_account'),
    path('password_reset/', password_reset, name='password_reset'),
    path('password_reset_confirm/<str:token>/', password_reset_confirm, name='password_reset_confirm'),
    path('upload/', upload_view, name='upload'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('users/', user_list, name='user_list'),  # Kullanıcı listesi URL'si
    path('follow/<int:user_id>/', views.follow_unfollow, name='follow_unfollow'),
    path('followed_posts/', views.followed_posts, name='followed_posts'),  # Takip edilen kullanıcıların postları URL'si
    path('profile/', profile, name='profile'),  # Profil URL'si
]
