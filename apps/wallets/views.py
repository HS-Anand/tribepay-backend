from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.exceptions import ValidationError

from .models import Wallet
from .serializers import WalletSerializer

from apps.wallets.serializers import AddMoneySerializer
from apps.wallets.services.add_money_service import add_money


class MyWalletsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        wallets = Wallet.objects.filter(
            memberships__user=request.user
        ).distinct()

        serializer = WalletSerializer(wallets, many=True)

        return Response(serializer.data)
    

class AddMoneyView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = AddMoneySerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:

            wallet, transaction_obj = add_money(
                user=request.user,
                amount=serializer.validated_data["amount"]
            )

            return Response(
                {
                    "message": "Money added successfully.",
                    "wallet_balance": wallet.balance,
                    "transaction_id": transaction_obj.tid
                },
                status=status.HTTP_200_OK
            )

        except ValidationError as e:

            return Response(
                {
                    "error": e.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )