from rest_framework import serializers

from apps.invoices.models import CashInvoice


class CreateInvoiceSerializer(serializers.Serializer):

    payer_username = serializers.CharField(
        max_length=150
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    description = serializers.CharField(
        max_length=40
    )


class InvoiceSerializer(serializers.ModelSerializer):

    created_by = serializers.CharField(
        source="created_by.username"
    )

    payer = serializers.CharField(
        source="payer.username"
    )

    class Meta:

        model = CashInvoice

        fields = [
            "iid",
            "created_by",
            "payer",
            "amount",
            "description",
            "invoice_type",
            "status",
            "created_at",
            "paid_at",
        ]


class PayInvoiceSerializer(serializers.Serializer):

    invoice_id = serializers.UUIDField()


class RejectInvoiceSerializer(serializers.Serializer):

    invoice_id = serializers.UUIDField()