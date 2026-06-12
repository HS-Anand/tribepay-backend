from decimal import Decimal
import uuid
import threading

from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError

from apps.wallets.models import (
    Wallet,
    WalletMembership
)
from django.db import connection

from apps.transactions.models import Transaction

from apps.wallets.services.transfer_service import (
    transfer_funds
)


User = get_user_model()


class TransferConcurrencyTest(TransactionTestCase):

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

    def test_concurrent_double_spend_prevention(self):

        print(
            "\n\n===== TEST: CONCURRENT DOUBLE SPEND PREVENTION ====="
        )

        errors = []

        def attempt_transfer():

            try:

                transfer_funds(
                    initiated_by_user=self.user1,
                    sender_wallet_id=self.wallet1.wid,
                    receiver_wallet_id=self.wallet2.wid,
                    amount=Decimal("800.00"),
                    idempotency_key=uuid.uuid4()
                )

            except ValidationError as e:

                errors.append(e)

            finally:
                connection.close()

        thread1 = threading.Thread(
            target=attempt_transfer
        )

        thread2 = threading.Thread(
            target=attempt_transfer
        )

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()

        self.assertEqual(Transaction.objects.count(), 1)

        self.assertEqual(len(errors), 1)

        self.assertEqual(self.wallet1.balance, Decimal("200.00"))

        self.assertEqual(self.wallet2.balance, Decimal("800.00"))