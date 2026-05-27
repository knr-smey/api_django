from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from dj_rest_auth.registration.views import SocialLoginView

User = get_user_model()


class GoogleLogin(SocialLoginView):

    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    callback_url = (
        "http://127.0.0.1:8000/accounts/google/login/callback/"
    )

    def pre_social_login(
        self,
        request,
        sociallogin
    ):

        email = sociallogin.user.email

        if not email:
            return

        user_exists = User.objects.filter(
            email=email
        ).exists()

        social_exists = SocialAccount.objects.filter(
            user__email=email,
            provider="google"
        ).exists()

        if user_exists and not social_exists:

            raise ValidationError({
                "message":
                "Account already exists. Please sign in instead."
            })