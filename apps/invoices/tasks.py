from celery import shared_task

from django.utils import timezone

from datetime import timedelta

from apps.invoices.models import CashInvoice

from apps.notifications.services import create_notification


@shared_task
def expire_pending_invoices():

    invoices = (
        CashInvoice.objects
        .select_related(
            "payer",
            "created_by"
        )
        .filter(
            status="PENDING",
            expires_at__lt=timezone.now()
        )
    )

    count = 0

    for invoice in invoices:

        invoice.status = "EXPIRED"

        invoice.save(
            update_fields=["status"]
        )

        create_notification(
            user=invoice.payer,
            message=(
                f"Your invoice of ₹{invoice.amount} "
                f"from {invoice.created_by.username} "
                f"has expired."
            )
        )

        create_notification(
            user=invoice.created_by,
            message=(
                f"Your invoice request of "
                f"₹{invoice.amount} to "
                f"{invoice.payer.username} "
                f"has expired."
            )
        )

        count += 1

    return f"{count} invoices expired."


@shared_task
def send_invoice_expiry_reminders():

    now = timezone.now()

    reminder_limit = now + timedelta(days=1)

    invoices = (
        CashInvoice.objects
        .select_related(
            "payer",
            "created_by"
        )
        .filter(
            status="PENDING",
            expires_at__gt=now,
            expires_at__lte=reminder_limit,
            reminder_sent=False
        )
    )

    count = 0

    for invoice in invoices:

        create_notification(
            user=invoice.payer,
            message=(
                f"Reminder: Your invoice of "
                f"₹{invoice.amount} from "
                f"{invoice.created_by.username} "
                f"is expiring soon."
            )
        )

        create_notification(
            user=invoice.created_by,
            message=(
                f"Reminder: Your invoice request "
                f"of ₹{invoice.amount} to "
                f"{invoice.payer.username} "
                f"is expiring soon."
            )
        )

        CashInvoice.objects.filter(
            iid=invoice.iid
        ).update(
            reminder_sent=True
        )

        count += 1

    return f"{count} invoice reminders sent."