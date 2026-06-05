from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.wallets.models import Wallet
from apps.transactions.models import Transaction
from apps.notifications.services import create_notification


def add_money(
    user,
    amount
):

    amount = Decimal(amount)

    if amount <= 0:
        raise ValidationError("Amount must be positive.")

    with transaction.atomic():

        wallet = Wallet.objects.select_for_update().get(
            memberships__user=user,
            wallet_type="PRS"
        )

        wallet.balance += amount
        wallet.save()

        transaction_obj = Transaction.objects.create(
            initiated_by_user=user,
            sender_wallet=wallet,
            receiver_wallet=wallet,
            amount=amount,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            status=Transaction.Status.SUCCESS
        )
        create_notification(
            user=user,
            message=(
                f"₹{amount} added successfully "
                f"to your wallet."
            )
        )

        return wallet, transaction_obj