from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.wallets.services.transfer_service import transfer_funds
from apps.splits.services.split_service import create_split


@transaction.atomic
def smart_payment(
    initiated_by_user,
    sender_wallet_id,
    receiver_wallet_id,
    amount,
    is_split=False,
    split_type=None,
    split_title=None,
    members=None
):

    payment_transaction = transfer_funds(
        initiated_by_user=initiated_by_user,
        sender_wallet_id=sender_wallet_id,
        receiver_wallet_id=receiver_wallet_id,
        amount=amount
    )

    split = None

    if is_split:

        if not split_type:
            raise ValidationError("Split type required.")

        if not split_title:
            raise ValidationError("Split title required.")

        if not members:
            raise ValidationError("Split members required.")

        split = create_split(
            created_by=initiated_by_user,
            total_amount=amount,
            title=split_title,
            split_type=split_type,
            members=members
        )

        split.transaction = payment_transaction
        split.save(update_fields=["transaction"])

    return {
        "transaction": payment_transaction,
        "split": split
    }