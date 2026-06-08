from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter
)

from apps.settlements.serializers import (
    SettlementPreviewSerializer,
    ExecuteSettlementSerializer
)
from apps.settlements.services.settlement_service import (
    preview_settlement,
    execute_settlement
)


@extend_schema_view(
    get=extend_schema(
        tags=["Settlements"],
        parameters=[
            OpenApiParameter(
                name="username",
                type=str,
                required=True,
                description="User to settle with"
            )
        ],
        responses=SettlementPreviewSerializer
    )
)
class SettlementPreviewView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        username = request.query_params.get("username")

        result = preview_settlement(
            user=request.user,
            other_username=username
        )

        serializer = SettlementPreviewSerializer(result)

        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        tags=["Settlements"],
        request=ExecuteSettlementSerializer
    )
)
class ExecuteSettlementView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ExecuteSettlementSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        txn = execute_settlement(
            user=request.user,
            other_username=serializer.validated_data["username"]
        )

        return Response(
            {
                "message": "Settlement completed.",
                "transaction_id": txn.tid
            }
        )