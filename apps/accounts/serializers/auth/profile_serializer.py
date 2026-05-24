from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined"
        )