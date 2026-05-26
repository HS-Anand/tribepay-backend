from django.urls import path

from apps.transactions.views import TransferView


urlpatterns = [
    path(
        "transfer/",
        TransferView.as_view(),
        name="transfer"
    ),
]