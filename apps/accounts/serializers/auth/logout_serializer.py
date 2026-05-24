from rest_framework import serializers


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    def validate(self, attrs):

        if not attrs.get("refresh"):

            raise serializers.ValidationError(
                "Refresh token is required."
            )

        return attrs