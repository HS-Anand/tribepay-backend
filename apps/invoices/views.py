from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter
)

from apps.invoices.models import CashInvoice
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


User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        tags=["Invoices"],
        request=CreateInvoiceSerializer,
        responses=InvoiceSerializer
    )
)
class CreateInvoiceView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CreateInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payer = User.objects.get(
                username=serializer.validated_data["payer_username"]
            )

            invoice = create_invoice(
                created_by=request.user,
                payer=payer,
                amount=serializer.validated_data["amount"],
                description=serializer.validated_data["description"]
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=404
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=400
            )

        return Response(
            InvoiceSerializer(invoice).data,
            status=201
        )


@extend_schema_view(
    post=extend_schema(
        tags=["Invoices"],
        request=PayInvoiceSerializer,
        responses=InvoiceSerializer
    )
)
class PayInvoiceView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = PayInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            invoice = pay_invoice(
                user=request.user,
                invoice_id=serializer.validated_data["invoice_id"]
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=400
            )

        return Response(
            InvoiceSerializer(invoice).data
        )


@extend_schema_view(
    post=extend_schema(
        tags=["Invoices"]
    )
)
class RejectInvoiceView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        invoice = reject_invoice(
            user=request.user,
            invoice_id=request.data.get("invoice_id")
        )

        return Response(
            {
                "message": "Invoice rejected successfully",
                "invoice_id": str(invoice.iid),
                "status": invoice.status
            },
            status=200
        )


@extend_schema(
    tags=["Invoices"],
    parameters=[
        OpenApiParameter(
            name="role",
            type=str,
            required=False,
            description="Filter invoices by role: payer or creator"
        ),
        OpenApiParameter(
            name="status",
            type=str,
            required=False,
            description="Filter invoices by status"
        )
    ]
)
class InvoiceListView(ListAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = InvoiceSerializer

    def get_queryset(self):

        role = self.request.query_params.get("role")
        status = self.request.query_params.get("status")

        if role == "payer":
            invoices = CashInvoice.objects.filter(
                payer=self.request.user
            )

        elif role == "creator":
            invoices = CashInvoice.objects.filter(
                created_by=self.request.user
            )

        else:
            invoices = CashInvoice.objects.filter(
                Q(created_by=self.request.user)
                |
                Q(payer=self.request.user)
            )

        if status:
            invoices = invoices.filter(status=status)

        return invoices.order_by("-created_at")