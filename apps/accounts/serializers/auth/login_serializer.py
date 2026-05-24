from rest_framework import serializers

from apps.accounts.services.auth_service import (
    authenticate_user,
    issue_tokens
)


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        email = attrs.get(
            "email",
            ""
        ).lower()

        password = attrs.get(
            "password",
            ""
        )

        user = authenticate_user(
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Invalid credentials."
            )

        tokens = issue_tokens(user)

        return {
            "user": user,
            "tokens": tokens,
        }