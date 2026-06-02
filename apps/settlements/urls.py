from django.urls import path

from apps.settlements.views import (
    SettlementPreviewView,
    ExecuteSettlementView
)


urlpatterns = [
    path("preview/", SettlementPreviewView.as_view()),
    path("execute/", ExecuteSettlementView.as_view()),
]