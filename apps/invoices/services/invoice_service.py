from django.core.exceptions import ValidationError
from django.db import transaction

from apps.invoices.models import CashInvoice

from django.utils import timezone

import uuid
from apps.wallets.models import Wallet, WalletMembership

from apps.wallets.services.transfer_service import (
    transfer_funds
)


@transaction.atomic
def create_invoice(
    created_by,
    payer,
    amount,
    description
):

    if created_by == payer:

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

        description=description
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
            .get(
                iid=invoice_id
            )
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


    receiver_wallet = (
        WalletMembership.objects.select_related("wallet").get(
            user=invoice.created_by,
            wallet__wallet_type="PRS"
        ).wallet
    )

    idempotency_key = str(
        uuid.uuid4()
    )

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
            .get(
                iid=invoice_id
            )
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


    return invoice