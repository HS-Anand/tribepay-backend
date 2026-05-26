from decimal import Decimal

from rest_framework import serializers

from apps.transactions.models import Transaction


class TransferSerializer(serializers.Serializer):

    sender_wallet_id = serializers.UUIDField()

    receiver_wallet_id = serializers.UUIDField()

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01")
    )

    idempotency_key = serializers.UUIDField(
        required=False,
        allow_null=True
    )


class TransactionResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction

        fields = [
            "tid",
            "amount",
            "status",
            "sender_wallet",
            "receiver_wallet",
            "created_at"
        ]