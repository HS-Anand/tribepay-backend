from celery import shared_task

from django.utils import timezone

from apps.invoices.models import CashInvoice



@shared_task
def expire_pending_invoices():

    expired_count = (
        CashInvoice.objects
        .filter(
            status="PENDING",
            expires_at__lt=timezone.now()
        )
        .update(
            status="EXPIRED"
        )
    )


    return (
        f"{expired_count} invoices expired."
    )