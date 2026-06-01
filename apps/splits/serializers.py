from rest_framework import serializers

from apps.splits.models import (
    SplitPayment,
    SplitMember
)


class SplitMemberSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField(
        source="user.username"
    )


    class Meta:

        model = SplitMember

        fields = [

            "username",

            "share_amount",

            "is_payer",

            "invoice",
        ]



class SplitPaymentSerializer(
    serializers.ModelSerializer
):

    members = SplitMemberSerializer(
        many=True
    )


    created_by = serializers.CharField(
        source="created_by.username"
    )


    class Meta:

        model = SplitPayment

        fields = [

            "sid",

            "created_by",

            "total_amount",

            "title",

            "members",

            "created_at",
        ]

class SplitMemberInputSerializer(
    serializers.Serializer
):

    username = serializers.CharField()


    amount = serializers.DecimalField(

        max_digits=12,

        decimal_places=2,

        required=False
    )



class CreateSplitSerializer(
    serializers.Serializer
):

    total_amount = serializers.DecimalField(

        max_digits=12,

        decimal_places=2
    )


    title = serializers.CharField(

        max_length=50,

        required=False,

        allow_blank=True
    )


    split_type = serializers.ChoiceField(

        choices=[

            "EQUAL",

            "CUSTOM"
        ]
    )


    members = SplitMemberInputSerializer(

        many=True
    )