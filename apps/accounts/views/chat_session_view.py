from rest_framework.views import APIView

from apps.accounts.permissions import (
    IsAuthenticatedAndActive,
)

from apps.accounts.models import (
    ChatSession,
)

from apps.accounts.serializers import (
    ChatSessionSerializer,
)

from utils.responses import (
    success_response,
)


class ChatSessionAPIView(APIView):

    permission_classes = [
        IsAuthenticatedAndActive
    ]

    def get(self, request):

        sessions = ChatSession.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = ChatSessionSerializer(
            sessions,
            many=True
        )

        return success_response(
            serializer.data,
            "Chat sessions fetched"
        )