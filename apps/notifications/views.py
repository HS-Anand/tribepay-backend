from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationListView(ListAPIView):

    permission_classes = [
        IsAuthenticated
    ]

    serializer_class = NotificationSerializer


    def get_queryset(self):

        return (
            Notification.objects
            .filter(
                user=self.request.user,
                is_read=False
            )
            .order_by(
                "-created_at"
            )
        )



class MarkNotificationReadView(ListAPIView):

    permission_classes = [
        IsAuthenticated
    ]


    def patch(self, request, nid):

        notification = (
            Notification.objects.get(
                nid=nid,
                user=request.user
            )
        )


        notification.is_read = True

        notification.save()


        return Response(
            {
                "message": "Notification marked as read."
            }
        )