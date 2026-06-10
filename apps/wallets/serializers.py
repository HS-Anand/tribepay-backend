from rest_framework import serializers

from apps.wallets.models import Wallet



class WalletSerializer(
    serializers.ModelSerializer
):

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


class AddMoneySerializer(
    serializers.Serializer
):

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )


class CreateGroupWalletSerializer(
    serializers.Serializer
):

    group_name = serializers.CharField(
        max_length=100
    )


class JoinGroupSerializer(
    serializers.Serializer
):

    group_code = serializers.CharField(
        max_length=6
    )


class ApproveJoinRequestSerializer(
    serializers.Serializer
):

    request_id = serializers.UUIDField()


class PendingJoinRequestSerializer(
    serializers.Serializer
):

    request_id = serializers.UUIDField(
        source="rid"
    )

    username = serializers.CharField(
        source="requested_user.username"
    )

    status = serializers.CharField()


class MyGroupSerializer(
    serializers.Serializer
):

    wid = serializers.UUIDField(
        source="wallet.wid"
    )

    group_name = serializers.CharField(
        source="wallet.group_name"
    )

    group_code = serializers.CharField(
        source="wallet.group_code"
    )

    balance = serializers.DecimalField(
        source="wallet.balance",
        max_digits=12,
        decimal_places=2
    )

    role = serializers.CharField()

    members_count = serializers.IntegerField(
        source="wallet.member_count"
    )


class GroupMemberSerializer(
    serializers.Serializer
):

    username = serializers.CharField(
        source="user.username"
    )

    role = serializers.CharField()


class GroupTransactionSerializer(
    serializers.Serializer
):

    transaction_id = serializers.UUIDField(
        source="tid"
    )

    sender_wallet_id = serializers.UUIDField(
        source="sender_wallet.wid"
    )

    receiver_wallet_id = serializers.UUIDField(
        source="receiver_wallet.wid"
    )

    sender_wallet_type = serializers.CharField(
        source="sender_wallet.wallet_type"
    )

    receiver_wallet_type = serializers.CharField(
        source="receiver_wallet.wallet_type"
    )

    initiated_by = serializers.CharField(
        source="initiated_by_user.username"
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    transaction_type = serializers.CharField()

    created_at = serializers.DateTimeField()

class LeaveGroupSerializer(
    serializers.Serializer
):

    group_id = serializers.UUIDField()


class RemoveMemberSerializer(
    serializers.Serializer
):

    group_id = serializers.UUIDField()

    username = serializers.CharField()


class SmartPaymentMemberSerializer(serializers.Serializer):

    username = serializers.CharField()

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False
    )

class SmartPaymentSerializer(serializers.Serializer):

    receiver_username = serializers.CharField()

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    is_split = serializers.BooleanField(
        default=False
    )

    split_title = serializers.CharField(
        required=False
    )

    split_type = serializers.ChoiceField(
        choices=[
            "EQUAL",
            "CUSTOM"
        ],
        required=False
    )

    members = SmartPaymentMemberSerializer(
        many=True,
        required=False
    )