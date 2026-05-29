import uuid
from django.db import models
from apps.wallets.models import Wallet
from django.conf import settings


class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        TRANSFER = "TRANSFER", "Transfer"
        DEPOSIT = "DEPOSIT", "Deposit"
        GROUP_CONTRIBUTION = "GROUP_CONTRIBUTION", "Group Contribution"
        GROUP_EXPENSE = "GROUP_EXPENSE", "Group Expense"
        WITHDRAWAL = "WITHDRAWAL", "Withdrawal"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    tid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    initiated_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiated_transactions"
    )

    sender_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="sent_transactions"
    )

    receiver_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="received_transactions"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.TRANSFER
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    idempotency_key = models.UUIDField(
        unique=True,
        null=True,
        blank=True
    )

    reference_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="amount_must_be_positive"
            )
        ]
     


    def __str__(self):
        return f"{self.reference_id} - {self.status}"