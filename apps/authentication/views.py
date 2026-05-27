from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import SignupSerializer


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
    
from rest_framework.permissions import IsAuthenticated


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "user_id": str(request.user.uid),
            "username": request.user.username,
            "email": request.user.email,
        })