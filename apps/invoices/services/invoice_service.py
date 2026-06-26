from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.invoices.models import CashInvoice
from apps.notifications.services import create_notification
from apps.wallets.models import WalletMembership

import uuid

from apps.wallets.services.transfer_service import (
    transfer_funds
)


@transaction.atomic
def create_invoice(
    created_by,
    payer,
    amount,
    description,
    invoice_type="REQUEST",
    target_wallet = None
):

    if created_by == payer and not target_wallet:

        raise ValidationError(
            "Cannot create invoice for yourself."
        )

    if amount <= 0:

        raise ValidationError(
            "Amount must be greater than zero."
        )

    invoice = CashInvoice.objects.create(
        created_by=created_by,
        payer=payer,
        amount=amount,
        description=description,
        invoice_type=invoice_type,
        target_wallet = target_wallet
    )

    if target_wallet:

        message = (
            f"{created_by.username} requested "
            f"₹{amount} for group "
            f"{target_wallet.group_name}."
        )

    elif invoice_type == "REQUEST":

        message = (
            f"{created_by.username} requested "
            f"₹{amount} from you."
        )

    elif invoice_type == "EXPENSE":

        message = (
            f"{created_by.username} added "
            f"₹{amount} expense for you."
        )

    create_notification(
        user=payer,
        message=message
    )

    return invoice


@transaction.atomic
def pay_invoice(
    user,
    invoice_id
):

    try:

        invoice = (
            CashInvoice.objects
            .select_for_update()
            .get(iid=invoice_id)
        )

    except CashInvoice.DoesNotExist:

        raise ValidationError(
            "Invoice not found."
        )

    if invoice.status != "PENDING":

        raise ValidationError(
            "Invoice already processed."
        )

    if invoice.payer != user:

        raise ValidationError(
            "You cannot pay this invoice."
        )

    payer_wallet = (
        WalletMembership.objects.select_related("wallet").get(
            user=user,
            wallet__wallet_type="PRS"
        ).wallet
    )

    if invoice.target_wallet:
        receiver_wallet = invoice.target_wallet

    else:
        receiver_wallet = (
            WalletMembership.objects.select_related("wallet").get(
                user=invoice.created_by,
                wallet__wallet_type="PRS"
            ).wallet
        )

    idempotency_key = str(uuid.uuid4())

    txn = transfer_funds(
        sender_wallet_id=payer_wallet.wid,
        receiver_wallet_id=receiver_wallet.wid,
        amount=invoice.amount,
        initiated_by_user=user,
        idempotency_key=idempotency_key
    )

    invoice.status = "PAID"
    
    invoice.transaction = txn

    invoice.paid_at = timezone.now()

    invoice.save()

    create_notification(
        user=invoice.created_by,
        message=(
            f"{user.username} paid your "
            f"₹{invoice.amount} invoice."
        )
    )


    return invoice


@transaction.atomic
def reject_invoice(
    user,
    invoice_id
):

    try:

        invoice = (
            CashInvoice.objects
            .select_for_update()
            .get(iid=invoice_id)
        )

    except CashInvoice.DoesNotExist:

        raise ValidationError(
            "Invoice not found."
        )


    if invoice.status != "PENDING":

        raise ValidationError(
            "Invoice already processed."
        )


    if invoice.payer != user:

        raise ValidationError(
            "You cannot reject this invoice."
        )


    invoice.status = "REJECTED"

    invoice.save(
        update_fields=["status"]
    )

    create_notification(

        user=invoice.created_by,

        message=(
            f"{user.username} rejected your "
            f"₹{invoice.amount} invoice."
        )
    )


    return invoice