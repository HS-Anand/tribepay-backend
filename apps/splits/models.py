import uuid

from django.db import models
from django.conf import settings


class SplitPayment(models.Model):


    sid = models.UUIDField(

        primary_key=True,

        default=uuid.uuid4,

        editable=False
    )


    created_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="created_splits"
    )


    transaction = models.OneToOneField(

        "transactions.Transaction",

        on_delete=models.SET_NULL,

        null=True,

        blank=True
    )


    total_amount = models.DecimalField(

        max_digits=12,

        decimal_places=2
    )


    title = models.CharField(

        max_length=50,

        blank=True
    )


    created_at = models.DateTimeField(

        auto_now_add=True
    )


    def __str__(self):

        return (
            f"{self.title} - {self.total_amount}"
        )



class SplitMember(models.Model):


    split = models.ForeignKey(

        SplitPayment,

        on_delete=models.CASCADE,

        related_name="members"
    )


    user = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="split_memberships"
    )


    share_amount = models.DecimalField(

        max_digits=12,

        decimal_places=2
    )


    is_payer = models.BooleanField(

        default=False
    )


    invoice = models.OneToOneField(

        "invoices.CashInvoice",

        on_delete=models.SET_NULL,

        null=True,

        blank=True
    )


    created_at = models.DateTimeField(

        auto_now_add=True
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "split",
                    "user"
                ],

                name="unique_split_member"
            )
        ]


    def __str__(self):

        return (
            f"{self.user.username}: {self.share_amount}"
        )