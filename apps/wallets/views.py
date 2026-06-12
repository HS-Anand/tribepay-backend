from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view
)

from apps.transactions.models import Transaction

from .models import (
    Wallet,
    WalletMembership,
    GroupJoinRequest
)

from apps.wallets.services.smart_payment_service import smart_payment

from apps.wallets.services.add_money_service import add_money

from apps.wallets.services.group_wallet_service import (
    create_group_wallet,
    request_join_group,
    approve_join_request,
    reject_join_request,
    leave_group,
    remove_member
)

from apps.wallets.serializers import (
    WalletSerializer,
    AddMoneySerializer,
    CreateGroupWalletSerializer,
    JoinGroupSerializer,
    ApproveJoinRequestSerializer,
    MyGroupSerializer,
    GroupMemberSerializer,
    GroupTransactionSerializer,
    PendingJoinRequestSerializer,
    LeaveGroupSerializer,
    RemoveMemberSerializer,
    SmartPaymentSerializer
)


User = get_user_model()


@extend_schema_view(
    get=extend_schema(
        tags=["Wallets"],
        responses=WalletSerializer
    )
)
class MyWalletsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        wallets = Wallet.objects.filter(
            memberships__user=request.user
        ).distinct()

        serializer = WalletSerializer(wallets, many=True)

        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        tags=["Wallets"],
        request=AddMoneySerializer,
        responses=WalletSerializer
    )
)
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
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
@extend_schema_view(
    post=extend_schema(
        tags=["Groups"],
        request=CreateGroupWalletSerializer,
        responses=WalletSerializer
    )
)
class CreateGroupWalletView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CreateGroupWalletSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        wallet = create_group_wallet(
            user=request.user,
            group_name=serializer.validated_data["group_name"]
        )

        return Response(
            {
                "message": "Group wallet created successfully.",
                "wallet": {
                    "wid": str(wallet.wid),
                    "group_name": wallet.group_name,
                    "group_code": wallet.group_code,
                    "wallet_type": wallet.wallet_type,
                    "balance": str(wallet.balance)
                }
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema_view(
    post=extend_schema(
        tags=["Groups"],
        request=JoinGroupSerializer
    )
)
class JoinGroupView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = JoinGroupSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        join_request = request_join_group(
            user=request.user,
            group_code=serializer.validated_data["group_code"]
        )

        return Response(
            {
                "message": "Join request sent successfully.",
                "request": {
                    "rid": str(join_request.rid),
                    "requested_by": join_request.requested_user.username,
                    "group_name": join_request.wallet.group_name,
                    "group_code": join_request.wallet.group_code,
                    "status": join_request.status
                }
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema_view(
    post=extend_schema(
        tags=["Groups"],
        request=ApproveJoinRequestSerializer
    )
)
class ApproveJoinRequestView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ApproveJoinRequestSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        join_request = approve_join_request(
            owner_user=request.user,
            request_id=serializer.validated_data["request_id"]
        )

        return Response(
            {
                "message": "Member approved successfully.",
                "member": {
                    "username": join_request.requested_user.username,
                    "group_name": join_request.wallet.group_name,
                    "group_code": join_request.wallet.group_code,
                    "status": join_request.status
                }
            },
            status=status.HTTP_200_OK
        )
    
@extend_schema_view(
    get=extend_schema(
        tags=["Groups"],
        responses=MyGroupSerializer
    )
)
class MyGroupsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        memberships = (
            WalletMembership.objects
            .select_related("wallet")
            .filter(
                user=request.user,
                wallet__wallet_type="GRP"
            )
        )

        response_data = []

        for membership in memberships:

            wallet = membership.wallet

            wallet.member_count = wallet.memberships.count()

            response_data.append({
                "wallet": wallet,
                "role": membership.role
            })

        serializer = MyGroupSerializer(response_data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        tags=["Groups"],
        responses=GroupMemberSerializer
    )
)
class GroupMembersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, wid):

        try:

            wallet = Wallet.objects.get(
                wid=wid,
                wallet_type="GRP"
            )

        except Wallet.DoesNotExist:

            return Response(
                {"error": "Group wallet not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        membership_exists = WalletMembership.objects.filter(
            user=request.user,
            wallet=wallet
        ).exists()

        if not membership_exists:

            return Response(
                {"error": "You are not a member of this group"},
                status=status.HTTP_403_FORBIDDEN
            )

        memberships = (
            WalletMembership.objects
            .select_related("user")
            .filter(wallet=wallet)
        )

        serializer = GroupMemberSerializer(
            memberships,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    get=extend_schema(
        tags=["Groups"],
        responses=GroupTransactionSerializer
    )
)
class GroupTransactionsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, wid):

        try:

            wallet = Wallet.objects.get(
                wid=wid,
                wallet_type="GRP"
            )

        except Wallet.DoesNotExist:

            return Response(
                {"error": "Group wallet not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        membership_exists = WalletMembership.objects.filter(
            user=request.user,
            wallet=wallet
        ).exists()

        if not membership_exists:

            return Response(
                {"error": "You are not a member of this group"},
                status=status.HTTP_403_FORBIDDEN
            )

        transactions = (
            Transaction.objects
            .select_related(
                "sender_wallet",
                "receiver_wallet",
                "initiated_by_user"
            )
            .filter(
                Q(sender_wallet=wallet) |
                Q(receiver_wallet=wallet)
            )
            .order_by("-created_at")
        )

        serializer = GroupTransactionSerializer(
            transactions,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
@extend_schema_view(
    get=extend_schema(
        tags=["Groups"],
        responses=PendingJoinRequestSerializer
    )
)
class PendingJoinRequestsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, wid):

        wallet = get_object_or_404(
            Wallet,
            wid=wid,
            wallet_type="GRP"
        )

        owner_membership = (
            WalletMembership.objects.filter(
                wallet=wallet,
                user=request.user,
                role="OWNER"
            ).exists()
        )

        if not owner_membership:

            return Response(
                {"error": "Only owner can view requests."},
                status=403
            )

        requests = (
            GroupJoinRequest.objects.filter(
                wallet=wallet,
                status="PENDING"
            )
            .select_related("requested_user")
            .order_by("-created_at")
        )

        serializer = PendingJoinRequestSerializer(
            requests,
            many=True
        )

        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        tags=["Groups"],
        request=ApproveJoinRequestSerializer
    )
)
class RejectJoinRequestView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ApproveJoinRequestSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        join_request = reject_join_request(
            request_id=serializer.validated_data["request_id"],
            owner_user=request.user
        )

        return Response(
            {
                "message": "Request rejected.",
                "request_id": str(join_request.rid),
                "status": join_request.status
            }
        )


@extend_schema_view(
    post=extend_schema(
        tags=["Groups"],
        request=LeaveGroupSerializer
    )
)
class LeaveGroupView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = LeaveGroupSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        result = leave_group(
            user=request.user,
            group_id=serializer.validated_data["group_id"]
        )

        if result == "GROUP_CLOSED":

            return Response(
                {"message": "Group closed successfully."}
            )

        return Response(
            {"message": "Successfully left group."}
        )
    

@extend_schema_view(
    post=extend_schema(
        tags=["Groups"],
        request=RemoveMemberSerializer
    )
)
class RemoveMemberView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = RemoveMemberSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        remove_member(
            owner_user=request.user,
            group_id=serializer.validated_data["group_id"],
            username=serializer.validated_data["username"]
        )

        return Response(
            {"message": "Member removed successfully."}
        )


@extend_schema(
    tags=["Smart Payment"],
    request=SmartPaymentSerializer
)
class SmartPaymentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = SmartPaymentSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        receiver = User.objects.get(
            username=data["receiver_username"]
        )

        sender_wallet = Wallet.objects.get(
            wallet_type="PRS",
            memberships__user=request.user
        )

        receiver_wallet = Wallet.objects.get(
            wallet_type="PRS",
            memberships__user=receiver
        )

        result = smart_payment(
            initiated_by_user=request.user,
            sender_wallet_id=sender_wallet.wid,
            receiver_wallet_id=receiver_wallet.wid,
            amount=data["amount"],
            is_split=data.get("is_split", False),
            split_type=data.get("split_type"),
            split_title=data.get("split_title"),
            members=data.get("members")
        )

        return Response(
            {
                "message": "Payment successful",
                "transaction_id": str(result["transaction"].tid),
                "split_created": result["split"] is not None
            },
            status=status.HTTP_200_OK
        )