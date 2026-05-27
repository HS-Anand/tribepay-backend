from rest_framework import serializers
from apps.wallets.models import Wallet


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = [
            "wid",
            "wallet_type",
            "balance",
            "is_active",
            "created_at",
            "updated_at",
        ]




class AddMoneySerializer(serializers.Serializer):

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )