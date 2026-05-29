from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.wallets.models import Wallet
from apps.transactions.models import Transaction


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
    idempotency_key=None
):

    amount = Decimal(amount)

    # 1. Light Sanity Checks (Pre-Transaction)

    if sender_wallet_id == receiver_wallet_id:

        raise ValidationError(
            "Cannot transfer to same wallet."
        )

    if amount <= 0:

        raise ValidationError(
            "Amount must be positive."
        )

    # 2. Pure Idempotency Check

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

            # 3. Deterministic Deadlock Prevention Sorting

            wallet_ids = sorted([
                sender_wallet_id,
                receiver_wallet_id
            ])

            # 4. Strict Row Locking Sequence

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

                raise ValidationError(
                    "Wallet not found."
                )

            # 5. Lock-Protected Authorization & State Checks

            membership_exists = (
                sender_wallet.memberships.filter(
                    user=initiated_by_user
                ).exists()
            )

            if not membership_exists:

                raise UnauthorizedWalletException()

            if not sender_wallet.is_active:

                raise InactiveWalletException(
                    "Sender wallet is inactive."
                )

            if not receiver_wallet.is_active:

                raise InactiveWalletException(
                    "Receiver wallet is inactive."
                )

            if sender_wallet.balance < amount:

                raise InsufficientBalanceException()

            # 6. Balance Mutations

            sender_wallet.balance -= amount

            receiver_wallet.balance += amount

            sender_wallet.save()

            receiver_wallet.save()

            # 7. Transaction Type Resolution

            transaction_type = (
                Transaction.TransactionType.TRANSFER
            )

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

            # 8. Immutable Success Entry Creation

            return Transaction.objects.create(

                initiated_by_user=initiated_by_user,

                sender_wallet=sender_wallet,

                receiver_wallet=receiver_wallet,

                amount=amount,

                status=Transaction.Status.SUCCESS,

                transaction_type=transaction_type,

                idempotency_key=idempotency_key
            )

    # 9. Clean Rollback Scopes

    except InsufficientBalanceException:

        raise ValidationError(
            "Insufficient balance."
        )

    except UnauthorizedWalletException:

        raise ValidationError(
            "User not authorized for this wallet."
        )

    except InactiveWalletException as e:

        raise ValidationError(
            e.message
        )