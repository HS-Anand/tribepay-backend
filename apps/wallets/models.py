from decimal import Decimal
from django.conf import settings
from django.db import models
import uuid

class Wallet(models.Model):

    wid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    wallet_type = models.CharField(
        max_length=3,
        choices=[
            ("PRS", "Personal"),
            ("GRP", "Group"),
            ("OFN", "Offline"),
        ]
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WalletMembership(models.Model):

    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="wallet_memberships"
)

    wallet = models.ForeignKey(
    Wallet,
    on_delete=models.CASCADE,
    related_name="memberships"
)

    role = models.CharField(
        max_length=10,
        choices=[
            ("OWNER", "Owner"),
            ("MEMBER", "Member")
        ],
        default="MEMBER"
    )

    class Meta:
        unique_together = ("user", "wallet")

    def __str__(self):
        return f"{self.user.username} -> {self.wallet.wid}"