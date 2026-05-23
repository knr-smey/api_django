from django.urls import path

from apps.accounts.google_login import GoogleLogin

from apps.accounts.views import (
    ChatAPIView,
    LoginView,
    LogoutView,
    ProfileView,
    RefreshView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("profile/", ProfileView.as_view(), name="auth-profile"),
    path("google/", GoogleLogin.as_view(), name="auth-google"),
    path("chat/", ChatAPIView.as_view(), name="auth-chat"),
]