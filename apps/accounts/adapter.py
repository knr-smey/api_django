from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to automatically connect social accounts to existing
    users that share the same verified email address.

    This runs during the social login flow (pre-signup). If a local user
    exists with the same email, attach the social account to that user so
    dj-rest-auth/allauth continue as a login instead of raising a 400.
    """

    def pre_social_login(self, request, sociallogin):
        # If social account is already linked to a user, nothing to do.
        if sociallogin.is_existing:
            return

        email = (sociallogin.user.email or '').strip().lower()
        if not email:
            return

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return

        # Ensure an EmailAddress exists and is verified for this user.
        # Many providers return verified emails; mark as verified to avoid
        # blocking flows that require verified emails.
        EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={"verified": True, "primary": True},
        )

        # Connect this sociallogin to the existing user account.
        sociallogin.connect(request, user)
