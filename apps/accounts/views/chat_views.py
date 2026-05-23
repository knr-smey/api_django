from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.views import APIView

from apps.accounts.models import (
    ChatSession,
)

from apps.accounts.serializers import (
    ChatSerializer,
)

from apps.accounts.services.ai_service import (
    ask_ai,
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


class ChatAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

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

        # CREATE SESSION
        if not session_id:

            session = create_chat_session(
                request.user,
                message[:30]
            )

        else:

            session = ChatSession.objects.get(
                id=session_id,
                user=request.user
            )

        # SAVE USER MESSAGE
        save_message(
            request.user,
            session,
            "user",
            message
        )

        # LOAD CHAT HISTORY
        history = get_chat_history(
            session
        )

        # BUILD PROMPT
        prompt = ""

        for item in history:

            prompt += (
                f"{item.role}: "
                f"{item.content}\n"
            )

        # ASK AI
        ai_reply = ask_ai(prompt)

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