from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.invoices.models import CashInvoice

from apps.settlements.services.settlement_service import (
    preview_settlement
)

from apps.wallets.models import (
    Wallet,
    WalletMembership
)

from apps.transactions.models import Transaction

from apps.settlements.services.settlement_service import (
    preview_settlement,
    execute_settlement
)

User = get_user_model()


class SettlementTest(TestCase):

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
            balance=Decimal("0.00")
        )

        self.wallet2 = Wallet.objects.create(
            wallet_type="PRS",
            balance=Decimal("5000.00")
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
    
    
    def test_settlement_net_calculation(self):

        print(
            "\n\n===== TEST: SETTLEMENT NET CALCULATION ====="
        )


        CashInvoice.objects.create(
            created_by=self.user1,
            payer=self.user2,
            amount=Decimal("1500.00"),
            description="Hotel",
            status="PENDING",
            invoice_type="EXPENSE"
        )


        CashInvoice.objects.create(
            created_by=self.user1,
            payer=self.user2,
            amount=Decimal("500.00"),
            description="Food",
            status="PENDING",
            invoice_type="EXPENSE"
        )


        CashInvoice.objects.create(
            created_by=self.user2,
            payer=self.user1,
            amount=Decimal("400.00"),
            description="Taxi",
            status="PENDING",
            invoice_type="EXPENSE"
        )


        result = preview_settlement(
            user=self.user2,
            other_username=self.user1.username
        )


        self.assertEqual(
            result["amount"],
            Decimal("1600.00")
        )


        self.assertEqual(
            result["direction"],
            "YOU_OWE"
        )


        self.assertTrue(
            result["can_settle"]
        )


    def test_execute_settlement_updates_expense_invoices_only(self):

        print(
            "\n\n===== TEST: SETTLEMENT EXECUTION CONSISTENCY + REQUESTS UNTOUCHED ====="
        )


        expense1 = CashInvoice.objects.create(
            created_by=self.user1,
            payer=self.user2,
            amount=Decimal("1000.00"),
            description="Hotel",
            status="PENDING",
            invoice_type="EXPENSE"
        )


        expense2 = CashInvoice.objects.create(
            created_by=self.user1,
            payer=self.user2,
            amount=Decimal("500.00"),
            description="Food",
            status="PENDING",
            invoice_type="EXPENSE"
        )


        request_invoice = CashInvoice.objects.create(
            created_by=self.user1,
            payer=self.user2,
            amount=Decimal("200.00"),
            description="Normal request",
            status="PENDING",
            invoice_type="REQUEST"
        )


        txn = execute_settlement(
            user=self.user2,
            other_username=self.user1.username
        )


        expense1.refresh_from_db()
        expense2.refresh_from_db()
        request_invoice.refresh_from_db()


        self.assertEqual(
            expense1.status,
            "SETTLED"
        )

        self.assertEqual(
            expense2.status,
            "SETTLED"
        )


        self.assertEqual(
            expense1.transaction,
            txn
        )

        self.assertEqual(
            expense2.transaction,
            txn
        )


        self.assertEqual(
            request_invoice.status,
            "PENDING"
        )

        self.assertIsNone(
            request_invoice.transaction
        )


        self.assertEqual(
            Transaction.objects.count(),
            1
        )