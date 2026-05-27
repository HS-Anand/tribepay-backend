from django.urls import path
from .views import AddMoneyView, MyWalletsView


urlpatterns = [
    path("me/", MyWalletsView.as_view()),
    path("add-money/", AddMoneyView.as_view()),
]