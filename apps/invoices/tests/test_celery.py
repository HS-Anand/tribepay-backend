from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.invoices.models import CashInvoice

from apps.invoices.tasks import (
    expire_pending_invoices,
    send_invoice_expiry_reminders
)


User = get_user_model()


class InvoiceCeleryTest(TestCase):

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

    def test_expired_invoices_are_marked_expired(self):

        print(
            "\n\n===== TEST: CELERY INVOICE EXPIRY CORRECTNESS ====="
        )

        invoice = CashInvoice.objects.create(
            created_by=self.creator,
            payer=self.payer,
            amount=Decimal("500.00"),
            description="Dinner",
            status="PENDING",
            expires_at=timezone.now() - timedelta(days=1)
        )

        result = expire_pending_invoices()

        invoice.refresh_from_db()

        self.assertEqual(
            invoice.status,
            "EXPIRED"
        )

        self.assertEqual(
            result,
            "1 invoices expired."
        )

    @patch(
        "apps.invoices.tasks.create_notification"
    )
    def test_invoice_reminder_idempotency(
        self,
        mock_notification
    ):

        print(
            "\n\n===== TEST: CELERY REMINDER IDEMPOTENCY ====="
        )

        invoice = CashInvoice.objects.create(
            created_by=self.creator,
            payer=self.payer,
            amount=Decimal("500.00"),
            description="Dinner",
            status="PENDING",
            expires_at=timezone.now() + timedelta(hours=5),
            reminder_sent=False
        )

        first_run = send_invoice_expiry_reminders()
        second_run = send_invoice_expiry_reminders()

        invoice.refresh_from_db()

        self.assertTrue(
            invoice.reminder_sent
        )

        self.assertEqual(
            first_run,
            "1 invoice reminders sent."
        )

        self.assertEqual(
            second_run,
            "0 invoice reminders sent."
        )

        self.assertEqual(
            mock_notification.call_count,
            2
        )