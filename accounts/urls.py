from django.urls import path
from .views import register, login_view, home, welcome, activate_account, password_reset, password_reset_confirm

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', home, name='home'),
    path('welcome/', welcome, name='welcome'),
    path('activate/<str:code>/', activate_account, name='activate_account'),
    path('password_reset/', password_reset, name='password_reset'),
    path('password_reset_confirm/<str:token>/', password_reset_confirm, name='password_reset_confirm'),
]
