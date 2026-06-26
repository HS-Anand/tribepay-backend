from decimal import Decimal
import uuid

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.wallets.models import Wallet
from apps.transactions.models import Transaction
from apps.notifications.services import create_notification


class InsufficientBalanceException(Exception):
    pass


class UnauthorizedWalletException(Exception):
    pass


class InactiveWalletException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def transfer_funds(
    initiated_by_user,
    sender_wallet_id,
    receiver_wallet_id,
    amount,
    idempotency_key=None,
    transaction_type="TRANSFER"
):

    if idempotency_key is None:
        idempotency_key = str(uuid.uuid4())

    amount = Decimal(amount)

    if sender_wallet_id == receiver_wallet_id:
        raise ValidationError("Cannot transfer to same wallet.")

    if amount <= 0:
        raise ValidationError("Amount must be positive.")
    
    sender = Wallet.objects.get(
        wid = sender_wallet_id
    )
    if sender.wallet_type == "GRP":
        if sender.spending_limit is not None and amount>sender.spending_limit:
            raise ValidationError("Amount exceeds the group's spending limit.")

    if idempotency_key:

        existing_transaction = (
            Transaction.objects.filter(
                idempotency_key=idempotency_key,
                status=Transaction.Status.SUCCESS
            ).first()
        )

        if existing_transaction:
            return existing_transaction

    try:

        with transaction.atomic():

            wallet_ids = sorted(
                [
                    sender_wallet_id,
                    receiver_wallet_id
                ]
            )

            wallets = (
                Wallet.objects
                .select_for_update()
                .filter(
                    wid__in=wallet_ids
                )
                .order_by("wid")
            )

            sender_wallet = None
            receiver_wallet = None

            for wallet in wallets:

                if wallet.wid == sender_wallet_id:
                    sender_wallet = wallet

                elif wallet.wid == receiver_wallet_id:
                    receiver_wallet = wallet

            if not sender_wallet or not receiver_wallet:
                raise ValidationError("Wallet not found.")

            membership_exists = (
                sender_wallet
                .memberships
                .filter(
                    user=initiated_by_user
                )
                .exists()
            )

            if not membership_exists:
                raise UnauthorizedWalletException()

            if not sender_wallet.is_active:
                raise InactiveWalletException("Sender wallet is inactive.")

            if not receiver_wallet.is_active:
                raise InactiveWalletException("Receiver wallet is inactive.")

            if sender_wallet.balance < amount:
                raise InsufficientBalanceException()

            sender_wallet.balance -= amount
            receiver_wallet.balance += amount

            sender_wallet.save()
            receiver_wallet.save()

            if transaction_type == "TRANSFER":

                if (
                    sender_wallet.wallet_type == "PRS"
                    and
                    receiver_wallet.wallet_type == "GRP"
                ):

                    transaction_type = (
                        Transaction.TransactionType
                        .GROUP_CONTRIBUTION
                    )

                elif (
                    sender_wallet.wallet_type == "GRP"
                    and
                    receiver_wallet.wallet_type == "PRS"
                ):

                    transaction_type = (
                        Transaction.TransactionType
                        .GROUP_EXPENSE
                    )

            txn = Transaction.objects.create(
                initiated_by_user=initiated_by_user,
                sender_wallet=sender_wallet,
                receiver_wallet=receiver_wallet,
                amount=amount,
                status=Transaction.Status.SUCCESS,
                transaction_type=transaction_type,
                idempotency_key=idempotency_key,
            )

            if receiver_wallet.wallet_type == "PRS":

                receiver_member = (
                    receiver_wallet
                    .memberships
                    .first()
                )

                if (
                    receiver_member
                    and
                    receiver_member.user != initiated_by_user
                ):

                    create_notification(
                        user=receiver_member.user,
                        message=f"You received ₹{amount} from {initiated_by_user.username}."
                    )

            elif receiver_wallet.wallet_type == "GRP":

                group_members = (
                    receiver_wallet
                    .memberships
                    .exclude(
                        user=initiated_by_user
                    )
                )

                for member in group_members:

                    create_notification(
                        user=member.user,
                        message=f"{receiver_wallet.group_name} received ₹{amount} contribution from {initiated_by_user.username}."
                    )

            if sender_wallet.wallet_type == "GRP":

                group_members = (
                    sender_wallet
                    .memberships
                    .exclude(
                        user=initiated_by_user
                    )
                )

                for member in group_members:

                    create_notification(
                        user=member.user,
                        message=f"{initiated_by_user.username} spent ₹{amount} from {sender_wallet.group_name}."
                    )

            return txn

    except InsufficientBalanceException:

        raise ValidationError("Insufficient balance.")

    except UnauthorizedWalletException:

        raise ValidationError("User not authorized for this wallet.")

    except InactiveWalletException as e:

        raise ValidationError(e.message)