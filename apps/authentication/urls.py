from django.urls import path
from .views import LoginView, SignupView, MeView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("login/", LoginView.as_view(), name="login"),
]