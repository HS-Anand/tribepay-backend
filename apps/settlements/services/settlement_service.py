import uuid
from decimal import Decimal

from rest_framework.exceptions import ValidationError

from django.db import transaction
from django.db.models import Sum
from django.contrib.auth import get_user_model

from apps.invoices.models import CashInvoice
from apps.transactions.models import Transaction
from apps.wallets.models import WalletMembership
from apps.wallets.services.transfer_service import transfer_funds


User = get_user_model()


def preview_settlement(user, other_username):

    try:
        other_user = User.objects.get(
            username=other_username
        )

    except User.DoesNotExist:
        raise ValidationError("User not found.")

    if user == other_user:
        raise ValidationError(
            "Cannot settle with yourself."
        )

    they_owe = (
        CashInvoice.objects
        .filter(
            created_by=user,
            payer=other_user,
            status="PENDING",
            invoice_type="EXPENSE"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0")
    )

    you_owe = (
        CashInvoice.objects
        .filter(
            created_by=other_user,
            payer=user,
            status="PENDING",
            invoice_type="EXPENSE"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0")
    )

    net = you_owe - they_owe

    if net > 0:
        return {
            "user": other_user.username,
            "amount": net,
            "direction": "YOU_OWE",
            "can_settle": True
        }

    elif net < 0:
        return {
            "user": other_user.username,
            "amount": abs(net),
            "direction": "OWES_YOU",
            "can_settle": False
        }

    return {
        "user": other_user.username,
        "amount": Decimal("0"),
        "direction": "SETTLED",
        "can_settle": False
    }


@transaction.atomic
def execute_settlement(user, other_username):

    try:
        other_user = User.objects.get(
            username=other_username
        )

    except User.DoesNotExist:
        raise ValidationError("User not found.")

    if user == other_user:
        raise ValidationError(
            "Cannot settle with yourself."
        )

    they_owe_invoices = (
        CashInvoice.objects
        .select_for_update()
        .filter(
            created_by=user,
            payer=other_user,
            status="PENDING",
            invoice_type="EXPENSE"
        )
    )

    you_owe_invoices = (
        CashInvoice.objects
        .select_for_update()
        .filter(
            created_by=other_user,
            payer=user,
            status="PENDING",
            invoice_type="EXPENSE"
        )
    )

    they_owe = sum(
        invoice.amount
        for invoice in they_owe_invoices
    )

    you_owe = sum(
        invoice.amount
        for invoice in you_owe_invoices
    )

    net = you_owe - they_owe

    if net <= 0:
        raise ValidationError(
            "You do not owe this user money."
        )

    sender_wallet = (
        WalletMembership.objects
        .select_related("wallet")
        .get(
            user=user,
            wallet__wallet_type="PRS"
        )
        .wallet
    )

    receiver_wallet = (
        WalletMembership.objects
        .select_related("wallet")
        .get(
            user=other_user,
            wallet__wallet_type="PRS"
        )
        .wallet
    )

    txn = transfer_funds(
        sender_wallet_id=sender_wallet.wid,
        receiver_wallet_id=receiver_wallet.wid,
        amount=net,
        initiated_by_user=user,
        idempotency_key=str(uuid.uuid4()),
        transaction_type=Transaction.TransactionType.SETTLEMENT
    )

    all_invoices = (
        list(they_owe_invoices)
        +
        list(you_owe_invoices)
    )

    for invoice in all_invoices:
        invoice.status = "SETTLED"
        invoice.transaction = txn
        invoice.save()

    return txn