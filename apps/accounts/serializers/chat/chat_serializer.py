from rest_framework import serializers


class ChatSerializer(
    serializers.Serializer
):

    session_id = serializers.UUIDField(
        required=False,
        allow_null=True
    )

    message = serializers.CharField()