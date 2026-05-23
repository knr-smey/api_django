from ..models import ChatSession, UserHistory


def create_chat_session(user, title):

    return ChatSession.objects.create(
        user=user,
        title=title
    )


def save_message(
    user,
    session,
    role,
    content
):

    return UserHistory.objects.create(
        user=user,
        session=session,
        role=role,
        content=content
    )