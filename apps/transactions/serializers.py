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

    sender_username = serializers.SerializerMethodField()

    receiver_username = serializers.SerializerMethodField()

    class Meta:
        model = Transaction

        fields = [
            "tid",
            "transaction_type",
            "amount",
            "status",
            "sender_wallet",
            "receiver_wallet",
            "sender_username",
            "receiver_username",
            "created_at"
        ]

    def get_sender_username(self, obj):

        membership = obj.sender_wallet.memberships.first()

        if membership:
            return membership.user.username

        return "Unknown"

    def get_receiver_username(self, obj):

        membership = obj.receiver_wallet.memberships.first()

        if membership:
            return membership.user.username

        return "Unknown"
