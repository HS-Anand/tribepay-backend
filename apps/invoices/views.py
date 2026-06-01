from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.invoices.serializers import (
    CreateInvoiceSerializer,
    InvoiceSerializer,
    PayInvoiceSerializer
)

from apps.invoices.services.invoice_service import (
    create_invoice,
    pay_invoice,
    reject_invoice
)

from django.db.models import Q
from apps.invoices.models import CashInvoice


User = get_user_model()


class CreateInvoiceView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def post(
        self,
        request
    ):

        serializer = CreateInvoiceSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )


        try:

            payer = User.objects.get(
                username=serializer.validated_data[
                    "payer_username"
                ]
            )


            invoice = create_invoice(

                created_by=request.user,

                payer=payer,

                amount=serializer.validated_data[
                    "amount"
                ],

                description=serializer.validated_data[
                    "description"
                ]
            )


        except User.DoesNotExist:

            return Response(
                {
                    "error":
                    "User not found."
                },
                status=404
            )


        except ValidationError as e:

            return Response(
                {
                    "error":
                    str(e)
                },
                status=400
            )


        return Response(

            InvoiceSerializer(
                invoice
            ).data,

            status=201
        )
    
class PayInvoiceView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def post(
        self,
        request
    ):

        serializer = PayInvoiceSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )


        try:

            invoice = pay_invoice(

                user=request.user,

                invoice_id=serializer.validated_data[
                    "invoice_id"
                ],

                
            )


        except ValidationError as e:

            return Response(

                {
                    "error": str(e)
                },

                status=400
            )


        return Response(

            InvoiceSerializer(
                invoice
            ).data
        )
    
class RejectInvoiceView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def post(
        self,
        request
    ):

        invoice_id = request.data.get(
            "invoice_id"
        )


        invoice = reject_invoice(
            user=request.user,
            invoice_id=invoice_id
        )


        return Response(
            {
                "message": "Invoice rejected successfully",

                "invoice_id": str(
                    invoice.iid
                ),

                "status": invoice.status
            },
            status=200
        )
    
class InvoiceListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def get(
        self,
        request
    ):

        role = request.query_params.get(
            "role"
        )

        status = request.query_params.get(
            "status"
        )


        if role == "payer":

            invoices = CashInvoice.objects.filter(
                payer=request.user
            )


        elif role == "creator":

            invoices = CashInvoice.objects.filter(
                created_by=request.user
            )


        else:

            invoices = CashInvoice.objects.filter(
                Q(created_by=request.user)
                |
                Q(payer=request.user)
            )


        if status:

            invoices = invoices.filter(
                status=status
            )


        invoices = invoices.order_by(
            "-created_at"
        )


        serializer = InvoiceSerializer(
            invoices,
            many=True
        )


        return Response(
            serializer.data,
            status=200
        )