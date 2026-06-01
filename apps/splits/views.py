from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from apps.splits.serializers import (
    CreateSplitSerializer,
    SplitPaymentSerializer
)

from django.db.models import Q

from apps.splits.models import SplitPayment


from apps.splits.services.split_service import (
    create_split
)




class CreateSplitView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def post(
        self,
        request
    ):

        serializer = CreateSplitSerializer(
            data=request.data
        )


        serializer.is_valid(
            raise_exception=True
        )


        split = create_split(

            created_by=request.user,

            total_amount=serializer.validated_data[
                "total_amount"
            ],

            title=serializer.validated_data.get(
                "title",
                ""
            ),

            split_type=serializer.validated_data[
                "split_type"
            ],

            members=serializer.validated_data[
                "members"
            ]
        )


        return Response(

            SplitPaymentSerializer(split).data,

            status=201
        )
    
class SplitListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def get(
        self,
        request
    ):

        splits = (

            SplitPayment.objects.filter(

                Q(created_by=request.user)

                |

                Q(members__user=request.user)

            )

            .distinct()

            .order_by(
                "-created_at"
            )
        )


        serializer = SplitPaymentSerializer(

            splits,

            many=True
        )


        return Response(

            serializer.data,

            status=200
        )