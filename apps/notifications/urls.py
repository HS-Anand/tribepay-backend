from django.urls import path

from apps.notifications.views import (
    NotificationListView,
    MarkNotificationReadView
)


urlpatterns = [

    path("",NotificationListView.as_view()),
    path("<uuid:nid>/read/", MarkNotificationReadView.as_view()),
]