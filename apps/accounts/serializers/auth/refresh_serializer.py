from rest_framework import serializers

from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer
)


class RefreshSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    def validate(self, attrs):

        serializer = TokenRefreshSerializer(
            data=attrs
        )

        serializer.is_valid(
            raise_exception=True
        )

        return serializer.validated_data