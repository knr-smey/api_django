from rest_framework import status
from rest_framework.views import APIView

from apps.accounts.permissions import (
    IsAuthenticatedAndActive,
)

from apps.accounts.serializers import (
    ProfileSerializer,
)

from utils.responses import (
    success_response,
)

class ProfileView(APIView):

    permission_classes = [
        IsAuthenticatedAndActive
    ]

    def get(self, request):

        data = ProfileSerializer(
            request.user
        ).data

        return success_response(
            data,
            "Profile retrieved",
            status.HTTP_200_OK
        )