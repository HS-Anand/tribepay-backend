from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.transactions.models import Transaction
from apps.transactions.serializers import (
    TransferSerializer,
    TransactionResponseSerializer
)

from rest_framework.permissions import IsAuthenticated

from apps.wallets.services.transfer_service import transfer_funds


User = get_user_model()


class TransferView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = TransferSerializer()

        return Response(serializer.data)

    def post(self, request):

        serializer = TransferSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        initiated_by_user = request.user

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
        
class TransactionHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        transactions = Transaction.objects.filter(
            sender_wallet__memberships__user=request.user
        ) | Transaction.objects.filter(
            receiver_wallet__memberships__user=request.user
        )

        transactions = transactions.distinct().order_by("-created_at")

        serializer = TransactionResponseSerializer(
            transactions,
            many=True
        )

        return Response(serializer.data)