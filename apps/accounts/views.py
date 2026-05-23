from rest_framework import status
from rest_framework.permissions import AllowAny
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
	LogoutSerializer,
	ProfileSerializer,
	RefreshSerializer,
	RegisterSerializer,
)
from apps.accounts.throttles import LoginRateThrottle, RefreshRateThrottle, RegisterRateThrottle
from utils.responses import error_response, success_response


class RegisterView(APIView):
	permission_classes = [AllowAny]
	throttle_classes = [RegisterRateThrottle]

	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		if not serializer.is_valid():
			message = "Email already registered." if "email" in serializer.errors else "Validation error"
			return error_response(message, serializer.errors, status.HTTP_400_BAD_REQUEST)

		user = serializer.save()
		data = ProfileSerializer(user).data
		return success_response(data, "Registration successful", status.HTTP_201_CREATED)


class LoginView(APIView):
	permission_classes = [AllowAny]
	throttle_classes = [LoginRateThrottle]

	def post(self, request):
		email = request.data.get("email", "")
		ip_address = get_client_ip(request)
		if email and is_login_blocked(ip_address, email):
			response = error_response(
				"Too many requests. Please try again later.",
				status_code=status.HTTP_429_TOO_MANY_REQUESTS,
			)
			response["Retry-After"] = str(FAILED_LOGIN_WINDOW)
			return response

		serializer = LoginSerializer(data=request.data)
		if not serializer.is_valid():
			if email:
				record_failed_login(ip_address, email)
			return error_response("Invalid email or password.", status_code=status.HTTP_400_BAD_REQUEST)

		validated = serializer.validated_data
		if email:
			clear_failed_login(ip_address, email)
		response_data = {
			"user": ProfileSerializer(validated["user"]).data,
			"tokens": validated["tokens"],
		}
		return success_response(response_data, "Login successful", status.HTTP_200_OK)


class RefreshView(APIView):
	permission_classes = [AllowAny]
	throttle_classes = [RefreshRateThrottle]

	def post(self, request):
		serializer = RefreshSerializer(data=request.data)
		if not serializer.is_valid():
			return error_response("Invalid refresh token.", status_code=status.HTTP_400_BAD_REQUEST)

		return success_response(serializer.validated_data, "Token refreshed", status.HTTP_200_OK)


class LogoutView(APIView):
	permission_classes = [IsAuthenticatedAndActive]

	def post(self, request):
		serializer = LogoutSerializer(data=request.data)
		if not serializer.is_valid():
			return error_response("Logout failed", serializer.errors, status.HTTP_400_BAD_REQUEST)

		try:
			refresh = RefreshToken(serializer.validated_data["refresh"])
			refresh.blacklist()
		except Exception:
			return error_response("Invalid refresh token", status_code=status.HTTP_400_BAD_REQUEST)

		return success_response(message="Logout successful", status_code=status.HTTP_200_OK)


class ProfileView(APIView):
	permission_classes = [IsAuthenticatedAndActive]

	def get(self, request):
		data = ProfileSerializer(request.user).data
		return success_response(data, "Profile retrieved", status.HTTP_200_OK)
