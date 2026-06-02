from rest_framework import serializers



class SettlementPreviewSerializer(
    serializers.Serializer
):

    user = serializers.CharField()

    amount = serializers.DecimalField(

        max_digits=12,

        decimal_places=2
    )

    direction = serializers.CharField()

    can_settle = serializers.BooleanField()

class ExecuteSettlementSerializer(
    serializers.Serializer
):

    username = serializers.CharField()