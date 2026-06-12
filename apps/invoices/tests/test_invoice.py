from decimal import Decimal
import threading

from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import connection

from rest_framework.exceptions import ValidationError

from apps.wallets.models import (
    Wallet,
    WalletMembership
)

from apps.invoices.models import CashInvoice

from apps.invoices.services.invoice_service import (
    pay_invoice
)

from apps.transactions.models import Transaction


User = get_user_model()


class InvoiceConcurrencyTest(TransactionTestCase):

    def setUp(self):

        self.creator = User.objects.create_user(
            username="creator",
            phone_number="1111111111",
            password="1234"
        )

        self.payer = User.objects.create_user(
            username="payer",
            phone_number="2222222222",
            password="1234"
        )

        self.creator_wallet = Wallet.objects.create(
            wallet_type="PRS",
            balance=Decimal("0.00")
        )

        self.payer_wallet = Wallet.objects.create(
            wallet_type="PRS",
            balance=Decimal("1000.00")
        )

        WalletMembership.objects.create(
            user=self.creator,
            wallet=self.creator_wallet,
            role="OWNER"
        )

        WalletMembership.objects.create(
            user=self.payer,
            wallet=self.payer_wallet,
            role="OWNER"
        )

        self.invoice = CashInvoice.objects.create(
            created_by=self.creator,
            payer=self.payer,
            amount=Decimal("500.00"),
            description="Dinner",
            status="PENDING"
        )
    
    def test_invoice_double_payment_race(self):

        print(
            "\n\n===== TEST: INVOICE DOUBLE PAYMENT RACE PREVENTION ====="
        )

        errors = []

        def attempt_payment():

            try:

                pay_invoice(
                    user=self.payer,
                    invoice_id=self.invoice.iid
                )

            except ValidationError as e:

                errors.append(e)

            finally:

                connection.close()

        thread1 = threading.Thread(
            target=attempt_payment
        )

        thread2 = threading.Thread(
            target=attempt_payment
        )

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        self.invoice.refresh_from_db()
        self.creator_wallet.refresh_from_db()
        self.payer_wallet.refresh_from_db()

        self.assertEqual(
            self.invoice.status,
            "PAID"
        )

        self.assertEqual(
            Transaction.objects.count(),
            1
        )

        self.assertEqual(
            self.creator_wallet.balance,
            Decimal("500.00")
        )

        self.assertEqual(
            self.payer_wallet.balance,
            Decimal("500.00")
        )

    def test_invalid_invoice_state_transition(self):

        print(
            "\n\n===== TEST: INVALID INVOICE STATE TRANSITION ====="
        )

        self.invoice.status = "REJECTED"
        self.invoice.save()

        with self.assertRaises(ValidationError):

            pay_invoice(
                user=self.payer,
                invoice_id=self.invoice.iid
            )

        self.invoice.refresh_from_db()

        self.assertEqual(
            self.invoice.status,
            "REJECTED"
        )

        self.assertEqual(
            Transaction.objects.count(),
            0
        )