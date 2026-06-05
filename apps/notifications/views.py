from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def get(self, request):

        notifications = (
            Notification.objects
            .filter(
                user=request.user,
                is_read=False
            )
        )


        serializer = NotificationSerializer(

            notifications,

            many=True
        )


        return Response(
            serializer.data
        )



class MarkNotificationReadView(APIView):

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