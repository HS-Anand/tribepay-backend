from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view
)

from apps.users.models import User

from .serializers import (
    SignupSerializer,
    LoginSerializer
)


@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        request=SignupSerializer
    )
)
class SignupView(APIView):

    def post(self, request):

        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": "User created successfully",
                    "user_id": str(user.uid),
                    "username": user.username,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    get=extend_schema(
        tags=["Authentication"]
    )
)
class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response(
            {
                "user_id": str(request.user.uid),
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "phone_number": request.user.phone_number,
            }
        )


@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        request=LoginSerializer
    )
)
class LoginView(APIView):
    throttle_classes = [
        AnonRateThrottle
    ]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]

        try:

            user = User.objects.get(
                phone_number=phone_number
            )

        except User.DoesNotExist:

            return Response(
                {
                    "error": "Invalid phone number or PIN."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):

            return Response(
                {
                    "error": "Invalid phone number or PIN."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "username": user.username,
            },
            status=status.HTTP_200_OK
        )