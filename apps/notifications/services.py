from apps.notifications.models import Notification


def create_notification(user, message):

    notification = Notification.objects.create(

        user=user,

        message=message
    )


    return notification