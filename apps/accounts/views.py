from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.permissions import IsAuthenticatedAndActive
from apps.accounts.serializers import (
	LoginSerializer,
	LogoutSerializer,
	ProfileSerializer,
	RefreshSerializer,
	RegisterSerializer,
)
from utils.responses import error_response, success_response


class RegisterView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		if not serializer.is_valid():
			return error_response("Validation error", serializer.errors, status.HTTP_400_BAD_REQUEST)

		user = serializer.save()
		data = ProfileSerializer(user).data
		return success_response(data, "Registration successful", status.HTTP_201_CREATED)


class LoginView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		if not serializer.is_valid():
			return error_response("Login failed", serializer.errors, status.HTTP_400_BAD_REQUEST)

		validated = serializer.validated_data
		response_data = {
			"user": ProfileSerializer(validated["user"]).data,
			"tokens": validated["tokens"],
		}
		return success_response(response_data, "Login successful", status.HTTP_200_OK)


class RefreshView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = RefreshSerializer(data=request.data)
		if not serializer.is_valid():
			return error_response("Token refresh failed", serializer.errors, status.HTTP_400_BAD_REQUEST)

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
