from django.urls import path

from apps.transactions.views import TransactionHistoryView, TransferView


urlpatterns = [
    path(
        "transfer/",
        TransferView.as_view(),
        name="transfer"
    ),
    path("history/", TransactionHistoryView.as_view()),
]