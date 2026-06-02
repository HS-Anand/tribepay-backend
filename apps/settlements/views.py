from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.settlements.services.settlement_service import (
    preview_settlement,
    execute_settlement
)


from apps.settlements.serializers import (
    SettlementPreviewSerializer,
    ExecuteSettlementSerializer
)



class SettlementPreviewView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def get(
        self,
        request
    ):

        username = request.query_params.get(
            "username"
        )


        result = preview_settlement(

            user=request.user,

            other_username=username
        )


        serializer = SettlementPreviewSerializer(
            result
        )


        return Response(
            serializer.data
        )
    
class ExecuteSettlementView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def post(
        self,
        request
    ):


        serializer = ExecuteSettlementSerializer(

            data=request.data
        )


        serializer.is_valid(

            raise_exception=True
        )


        txn = execute_settlement(

            user=request.user,

            other_username=serializer.validated_data[
                "username"
            ]
        )


        return Response(

            {
                "message": "Settlement completed.",

                "transaction_id": txn.tid
            }
        )