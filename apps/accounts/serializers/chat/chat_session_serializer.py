from rest_framework import serializers

from apps.accounts.models import ChatSession


class ChatSessionSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = ChatSession

        fields = (
            "id",
            "title",
            "created_at",
        )