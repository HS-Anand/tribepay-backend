from decimal import Decimal
import uuid
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError

from apps.wallets.models import (
    Wallet,
    WalletMembership
)
from apps.transactions.models import Transaction
from apps.wallets.services.transfer_service import transfer_funds


User = get_user_model()


class TransferServiceTest(TestCase):

    def setUp(self):

        self.user1 = User.objects.create_user(
            username="user1",
            phone_number="1111111111",
            password="1234"
        )

        self.user2 = User.objects.create_user(
            username="user2",
            phone_number="2222222222",
            password="1234"
        )

        self.wallet1 = Wallet.objects.create(
            wallet_type="PRS",
            balance=Decimal("1000.00")
        )

        self.wallet2 = Wallet.objects.create(
            wallet_type="PRS",
            balance=Decimal("0.00")
        )

        WalletMembership.objects.create(
            user=self.user1,
            wallet=self.wallet1,
            role="OWNER"
        )

        WalletMembership.objects.create(
            user=self.user2,
            wallet=self.wallet2,
            role="OWNER"
        )


    def test_successful_transfer_updates_balance(self):

        print(
            "\n\n===== TEST: SUCCESSFUL TRANSFER & LEDGER CREATION ====="
        )

        transfer_funds(
            initiated_by_user=self.user1,
            sender_wallet_id=self.wallet1.wid,
            receiver_wallet_id=self.wallet2.wid,
            amount=Decimal("500.00"),
            idempotency_key=uuid.uuid4()
        )

        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()

        self.assertEqual(
            self.wallet1.balance,
            Decimal("500.00")
        )

        self.assertEqual(
            self.wallet2.balance,
            Decimal("500.00")
        )

        self.assertEqual(
            Transaction.objects.count(),
            1
        )


    def test_insufficient_balance_transfer_blocked(self):

        print(
        "\n\n===== TEST: INSUFFICIENT BALANCE PROTECTION ====="
        )


        with self.assertRaises(ValidationError):

            transfer_funds(
            initiated_by_user=self.user1,
            sender_wallet_id=self.wallet1.wid,
            receiver_wallet_id=self.wallet2.wid,
            amount=Decimal("2000.00"),
            idempotency_key=uuid.uuid4()
            )


        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()


        self.assertEqual(
        self.wallet1.balance,
        Decimal("1000.00")
        )


        self.assertEqual(
        self.wallet2.balance,
        Decimal("0.00")
        )


        self.assertEqual(
        Transaction.objects.count(),
        0
        )

    def test_total_balance_remains_constant_after_transfer(self):

        print(
        "\n\n===== TEST: BALANCE CONSERVATION INVARIANT ====="
        )


        before_total = (
        self.wallet1.balance +
        self.wallet2.balance
        )


        transfer_funds(
        initiated_by_user=self.user1,
        sender_wallet_id=self.wallet1.wid,
        receiver_wallet_id=self.wallet2.wid,
        amount=Decimal("300.00"),
        idempotency_key=uuid.uuid4()
        )


        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()


        after_total = (
        self.wallet1.balance +
        self.wallet2.balance
        )


        self.assertEqual(
        before_total,
        after_total
        )


    def test_idempotency_key_prevents_duplicate_transfer(self):

        print(
            "\n\n===== TEST: IDEMPOTENCY PROTECTION ====="
        )

        key = uuid.uuid4()

        first_transaction = transfer_funds(
            initiated_by_user=self.user1,
            sender_wallet_id=self.wallet1.wid,
            receiver_wallet_id=self.wallet2.wid,
            amount=Decimal("500.00"),
            idempotency_key=key
        )

        second_transaction = transfer_funds(
            initiated_by_user=self.user1,
            sender_wallet_id=self.wallet1.wid,
            receiver_wallet_id=self.wallet2.wid,
            amount=Decimal("500.00"),
            idempotency_key=key
        )

        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()

        self.assertEqual(
            first_transaction.tid,
            second_transaction.tid
        )

        self.assertEqual(
            self.wallet1.balance,
            Decimal("500.00")
        )

        self.assertEqual(
            self.wallet2.balance,
            Decimal("500.00")
        )

        self.assertEqual(
            Transaction.objects.count(),
            1
        )


    def test_transfer_rollback_on_failure(self):

        print(
            "\n\n===== TEST: ATOMIC ROLLBACK PROTECTION ====="
        )

        with patch(
            "apps.transactions.models.Transaction.objects.create"
        ) as mock_create:

            mock_create.side_effect = Exception(
                "Database failure"
            )

            try:

                transfer_funds(
                    initiated_by_user=self.user1,
                    sender_wallet_id=self.wallet1.wid,
                    receiver_wallet_id=self.wallet2.wid,
                    amount=Decimal("500.00"),
                    idempotency_key=uuid.uuid4()
                )

            except Exception:

                pass

        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()

        self.assertEqual(
            self.wallet1.balance,
            Decimal("1000.00")
        )

        self.assertEqual(
            self.wallet2.balance,
            Decimal("0.00")
        )

        self.assertEqual(
            Transaction.objects.count(),
            0
        )


    def test_user_cannot_spend_wallet_they_do_not_own(self):

        print(
            "\n\n===== TEST: UNAUTHORIZED WALLET ACCESS PREVENTION ====="
        )

        with self.assertRaises(ValidationError):

            transfer_funds(
                initiated_by_user=self.user2,
                sender_wallet_id=self.wallet1.wid,
                receiver_wallet_id=self.wallet2.wid,
                amount=Decimal("500.00"),
                idempotency_key=uuid.uuid4()
            )

        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()

        self.assertEqual(
            self.wallet1.balance,
            Decimal("1000.00")
        )

        self.assertEqual(
            self.wallet2.balance,
            Decimal("0.00")
        )

        self.assertEqual(
            Transaction.objects.count(),
            0
        )