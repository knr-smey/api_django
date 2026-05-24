from rest_framework import serializers

from apps.accounts.models import UserHistory


class ChatHistorySerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = UserHistory

        fields = (
            "id",
            "role",
            "content",
            "created_at",
        )