import uuid

from django.db import models
from django.conf import settings


class CashInvoice(models.Model):

    STATUS_CHOICES = [

        (
            "PENDING",
            "Pending"
        ),

        (
            "PAID",
            "Paid"
        ),

        (
            "REJECTED",
            "Rejected"
        ),

        (
            "EXPIRED",
            "Expired"
        ),

        (
            "SETTLED",
            "Settled"
        ),
    ]


    iid = models.UUIDField(

        primary_key=True,

        default=uuid.uuid4,

        editable=False
    )


    created_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="sent_invoices"
    )


    payer = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="received_invoices"
    )


    amount = models.DecimalField(

        max_digits=12,

        decimal_places=2
    )


    description = models.CharField(

        max_length=40
    )

    TYPE_CHOICES = [

        (
            "REQUEST",
            "Request"
        ),

        (
            "EXPENSE",
            "Expense"
        ),
    ]


    invoice_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="REQUEST"
    )

    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default="PENDING"
    )


    transaction = models.ForeignKey(

        "transactions.Transaction",

        on_delete=models.SET_NULL,

        null=True,

        blank=True
    )


    created_at = models.DateTimeField(

        auto_now_add=True
    )


    paid_at = models.DateTimeField(

        null=True,

        blank=True
    )


    def __str__(self):

        return (
            f"{self.created_by.username} -> "
            f"{self.payer.username}: {self.amount}"
        )