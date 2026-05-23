from ..models import UserHistory


def get_chat_history(session):

    return UserHistory.objects.filter(
        session=session
    ).order_by("created_at")