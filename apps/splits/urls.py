from django.urls import path

from apps.splits.views import (
    CreateSplitView,
    SplitListView
)


urlpatterns = [
    path("create/",CreateSplitView.as_view()),
    path("", SplitListView.as_view()),
]