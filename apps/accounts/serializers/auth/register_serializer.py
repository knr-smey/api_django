from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError
)

from rest_framework import serializers

from apps.accounts.services.auth_service import (
    create_user
)

from apps.accounts.validators import (
    validate_email_address,
    validate_password_strength
)

User = get_user_model()


class RegisterSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    password_confirm = serializers.CharField(
        write_only=True
    )

    first_name = serializers.CharField(
        required=False,
        allow_blank=True
    )

    last_name = serializers.CharField(
        required=False,
        allow_blank=True
    )

    def validate_email(self, value):

        email = value.strip().lower()

        validate_email_address(email)

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise serializers.ValidationError(
                "Email already exists."
            )

        return email

    def validate_password(self, value):

        validate_password_strength(value)

        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["password_confirm"]:

            raise serializers.ValidationError({
                "password_confirm":
                "Passwords do not match."
            })

        return attrs

    def create(self, validated_data):

        try:

            return create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=validated_data.get(
                    "first_name",
                    ""
                ),
                last_name=validated_data.get(
                    "last_name",
                    ""
                ),
            )

        except DjangoValidationError as exc:

            raise serializers.ValidationError({
                "email": [
                    "Email already exists."
                ]
            }) from exc