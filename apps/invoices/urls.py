from django.urls import path

from apps.invoices.views import (
    CreateInvoiceView,
    PayInvoiceView
)


urlpatterns = [
    path("create/", CreateInvoiceView.as_view()),
    path("pay/", PayInvoiceView.as_view()),
]