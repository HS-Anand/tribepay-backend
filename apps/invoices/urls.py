from django.urls import path

from apps.invoices.views import (
    CreateInvoiceView,
    PayInvoiceView,
    RejectInvoiceView,
    InvoiceListView
)


urlpatterns = [
    path("create/", CreateInvoiceView.as_view()),
    path("pay/", PayInvoiceView.as_view()),
    path("reject/", RejectInvoiceView.as_view(), name="reject-invoice"),
    path("",InvoiceListView.as_view()),
]