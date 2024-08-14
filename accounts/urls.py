from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('welcome/', views.welcome, name='welcome'),
    path('activate/<str:code>/', views.activate_account, name='activate_account'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_reset_confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('upload/', views.upload_view, name='upload'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('users/', views.user_list, name='user_list'),  # Kullanıcı listesi URL'si
    path('follow/<int:user_id>/', views.follow_unfollow, name='follow_unfollow'),
    path('followed_posts/', views.followed_posts, name='followed_posts'),  # Takip edilen kullanıcıların postları URL'si
    path('profile/', views.profile, name='profile'),  # Profil URL'si
    path('archive/<int:post_id>/', views.archive_post, name='archive_post'),

    # REST API endpointleri
    path('api/users/', views.UserList.as_view(), name='user-list'),
    path('api/posts/', views.PostList.as_view(), name='post-list'),
    path('api/posts/<int:pk>/', views.PostDetail.as_view(), name='post-detail'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
