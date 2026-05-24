from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.permissions import (
    IsAuthenticatedAndActive,
)

from apps.accounts.models import (
    ChatSession,
)

from apps.accounts.serializers import (
    ChatHistorySerializer,
)

from utils.responses import (
    success_response,
)


class ChatHistoryAPIView(APIView):

    permission_classes = [
        IsAuthenticatedAndActive
    ]

    def get(
        self,
        request,
        session_id
    ):

        try:

            session = ChatSession.objects.get(
                id=session_id,
                user=request.user
            )

        except ChatSession.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Session not found"
                },
                status=404
            )

        messages = session.messages.all()

        serializer = ChatHistorySerializer(
            messages,
            many=True
        )

        return success_response(
            serializer.data,
            "Chat history fetched"
        )