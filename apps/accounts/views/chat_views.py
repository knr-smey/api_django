import logging

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.permissions import (
    IsAuthenticatedAndActive,
)

from apps.accounts.models import (
    ChatSession,
)

from apps.accounts.serializers import (
    ChatSerializer,
)

from apps.accounts.services.ai_service import (
    generate_ai_reply,
)

from apps.accounts.services.chat_service import (
    create_chat_session,
    save_message,
)

from apps.accounts.services.history_service import (
    get_chat_history,
)

from utils.responses import (
    success_response,
)


logger = logging.getLogger(__name__)


class ChatAPIView(APIView):

    permission_classes = [
        IsAuthenticatedAndActive
    ]

    def post(self, request):

        try:

            serializer = ChatSerializer(
                data=request.data
            )

            serializer.is_valid(
                raise_exception=True
            )

            message = serializer.validated_data[
                "message"
            ]

            session_id = serializer.validated_data.get(
                "session_id"
            )

            # CREATE OR LOAD SESSION
            if not session_id:

                session = create_chat_session(
                    request.user,
                    message[:30]
                )

            else:

                try:

                    session = ChatSession.objects.get(
                        id=session_id,
                        user=request.user
                    )

                except ChatSession.DoesNotExist:

                    session = create_chat_session(
                        request.user,
                        message[:30]
                    )

            # SAVE USER MESSAGE
            save_message(
                request.user,
                session,
                "user",
                message
            )

            # LOAD HISTORY
            history = get_chat_history(
                session
            )

            # ASK AI
            ai_reply = generate_ai_reply(
                history
            )

            # SAVE AI RESPONSE
            save_message(
                request.user,
                session,
                "assistant",
                ai_reply
            )

            return success_response(
                {
                    "session_id": str(session.id),
                    "response": ai_reply,
                },
                "Chat response generated"
            )

        except Exception as e:

            logger.exception("Chat request failed")

            return Response(
                {
                    "success": False,
                    "message": str(e)
                },
                status=500
            )
