from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.wallets.models import Wallet, WalletMembership
from apps.wallets.services.smart_payment_service import smart_payment

from apps.splits.models import SplitPayment
from apps.invoices.models import CashInvoice


User = get_user_model()


class SmartPaymentTest(TestCase):

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

        self.user3 = User.objects.create_user(
            username="user3",
            phone_number="3333333333",
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
            wallet=self.wallet1,
            user=self.user1
        )

        WalletMembership.objects.create(
            wallet=self.wallet2,
            user=self.user2
        )


    def test_smart_payment_with_split_atomic_workflow(self):

        print(
            "\n\n===== TEST: SMART PAYMENT ATOMIC WORKFLOW ====="
        )


        result = smart_payment(
            initiated_by_user=self.user1,

            sender_wallet_id=self.wallet1.wid,

            receiver_wallet_id=self.wallet2.wid,

            amount=Decimal("900.00"),

            is_split=True,

            split_title="Dinner",

            split_type="EQUAL",

            members=[
                {
                    "username": self.user2.username
                },
                {
                    "username": self.user3.username
                }
            ]
        )


        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()

        self.assertEqual(
            self.wallet1.balance,
            Decimal("100.00")
        )

        self.assertEqual(
            self.wallet2.balance,
            Decimal("900.00")
        )


        transaction = result["transaction"]

        split = result["split"]

        self.assertIsNotNone(
            split
        )

        self.assertEqual(
            split.transaction,
            transaction
        )

        self.assertTrue(
            SplitPayment.objects.filter(
                transaction=transaction
            ).exists()
        )

        self.assertEqual(
            CashInvoice.objects.filter(
                invoice_type="EXPENSE"
            ).count(),
            2
        )