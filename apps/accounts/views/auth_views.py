from datetime import timedelta

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.permissions import IsAuthenticatedAndActive
from apps.accounts.security import (
    FAILED_LOGIN_WINDOW,
    clear_failed_login,
    get_client_ip,
    is_login_blocked,
    record_failed_login,
)

from apps.accounts.serializers import (
    LoginSerializer,
    RefreshSerializer,
    RegisterSerializer,
    ProfileSerializer,
)

from apps.accounts.throttles import (
    LoginRateThrottle,
    RefreshRateThrottle,
    RegisterRateThrottle,
)

from utils.responses import (
    error_response,
    success_response,
)


class RegisterView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            message = (
                "Email already registered."
                if "email" in serializer.errors
                else "Validation error"
            )

            return error_response(
                message,
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        # create tokens
        refresh = RefreshToken.for_user(user)

        response_data = {
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        }

        return success_response(
            response_data,
            "Registration successful",
            status.HTTP_201_CREATED
        )


class LoginView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):

        email = request.data.get("email", "")
        password = request.data.get("password", "")
        remember = request.data.get("remember", False)

        ip_address = get_client_ip(request)

        if email and is_login_blocked(ip_address, email):

            response = error_response(
                "Too many requests. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

            response["Retry-After"] = str(
                FAILED_LOGIN_WINDOW
            )

            return response

        serializer = LoginSerializer(
            data={
                "email": email,
                "password": password,
            }
        )

        if not serializer.is_valid():

            if email:
                record_failed_login(
                    ip_address,
                    email
                )

            return error_response(
                "Invalid email or password.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        validated = serializer.validated_data

        user = validated["user"]

        if email:
            clear_failed_login(
                ip_address,
                email
            )

        refresh = RefreshToken.for_user(user)

        if remember:

            refresh.set_exp(
                lifetime=timedelta(days=30)
            )

        else:

            refresh.set_exp(
                lifetime=timedelta(days=1)
            )

        response_data = {
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        }

        return success_response(
            response_data,
            "Login successful",
            status.HTTP_200_OK
        )


class RefreshView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [RefreshRateThrottle]

    def post(self, request):

        serializer = RefreshSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return error_response(
                "Invalid refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return success_response(
            serializer.validated_data,
            "Token refreshed",
            status.HTTP_200_OK
        )


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            refresh_token = request.data.get(
                "refresh"
            )

            token = RefreshToken(
                refresh_token
            )

            token.blacklist()

            return success_response(
                {},
                "Logout successful",
                status.HTTP_200_OK
            )

        except Exception:

            return error_response(
                "Logout failed",
                status_code=status.HTTP_400_BAD_REQUEST
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