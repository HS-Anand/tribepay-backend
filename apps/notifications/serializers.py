from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:

        model = Notification

        fields = [

            "nid",

            "message",

            "is_read",

            "created_at"

        ]