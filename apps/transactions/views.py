from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view
)

from apps.transactions.models import Transaction
from apps.transactions.serializers import (
    TransferSerializer,
    TransactionResponseSerializer
)
from apps.wallets.services.transfer_service import transfer_funds


User = get_user_model()


@extend_schema_view(
    get=extend_schema(
        tags=["Transactions"],
        responses=TransferSerializer
    ),
    post=extend_schema(
        tags=["Transactions"],
        request=TransferSerializer,
        responses=TransactionResponseSerializer
    )
)
class TransferView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = TransferSerializer()

        return Response(serializer.data)

    def post(self, request):

        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            transaction_obj = transfer_funds(
                initiated_by_user=request.user,
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
                {"error": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    tags=["Transactions"],
    responses=TransactionResponseSerializer
)
class TransactionHistoryView(ListAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = TransactionResponseSerializer

    def get_queryset(self):

        return (
            Transaction.objects
            .filter(
                Q(sender_wallet__memberships__user=self.request.user) |
                Q(receiver_wallet__memberships__user=self.request.user)
            )
            .distinct()
            .order_by("-created_at")
        )