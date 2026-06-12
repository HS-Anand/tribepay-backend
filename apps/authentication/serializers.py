import re

from rest_framework import serializers
from django.db import transaction
from apps.users.models import User
from apps.wallets.services.wallet_service import create_personal_wallet


class SignupSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "confirm_password",
        ]

        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_phone_number(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must be exactly 10 digits."
            )

        return value

    def validate_password(self, value):

        if not re.fullmatch(r"\d{6}", value):
            raise serializers.ValidationError(
                "PIN must be exactly 6 numeric digits."
            )

        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password": "PINs do not match."
                }
            )

        return attrs


    def create(self, validated_data):

        with transaction.atomic():
            validated_data.pop("confirm_password")

            first_name = validated_data["first_name"].lower()
            last_name = validated_data["last_name"].lower()

            username = (
                f"{first_name}_"
                f"{last_name}_"
                f"{validated_data['phone_number']}"
            )

            user = User.objects.create_user(
                username=username,
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                phone_number=validated_data["phone_number"],
                password=validated_data["password"],
            )

            create_personal_wallet(user)

            return user


class LoginSerializer(serializers.Serializer):

    phone_number = serializers.CharField()
    
    password = serializers.CharField(write_only=True)