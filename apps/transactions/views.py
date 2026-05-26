from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.transactions.serializers import (
    TransferSerializer,
    TransactionResponseSerializer
)

from apps.wallets.services.transfer_service import transfer_funds


User = get_user_model()


class TransferView(APIView):

    def get(self, request):

        serializer = TransferSerializer()

        return Response(serializer.data)

    def post(self, request):

        serializer = TransferSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        # temporary user for testing
        initiated_by_user = User.objects.first()

        try:

            transaction_obj = transfer_funds(
                initiated_by_user=initiated_by_user,
                sender_wallet_id=validated_data["sender_wallet_id"],
                receiver_wallet_id=validated_data["receiver_wallet_id"],
                amount=validated_data["amount"],
                idempotency_key=validated_data.get("idempotency_key")
            )

            response_serializer = TransactionResponseSerializer(
                transaction_obj
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:

            return Response(
                {
                    "error": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )