# from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError as DjangoValidationError
# from rest_framework import serializers
# from rest_framework_simplejwt.serializers import TokenRefreshSerializer

# from apps.accounts.services.auth_service  import authenticate_user, create_user, issue_tokens
# from apps.accounts.validators import validate_email_address, validate_password_strength

# User = get_user_model()


# class RegisterSerializer(serializers.Serializer):
# 	email = serializers.EmailField()
# 	password = serializers.CharField(write_only=True)
# 	password_confirm = serializers.CharField(write_only=True)
# 	first_name = serializers.CharField(required=False, allow_blank=True)
# 	last_name = serializers.CharField(required=False, allow_blank=True)

# 	def validate_email(self, value: str) -> str:
# 		email = value.strip().lower()
# 		validate_email_address(email)

# 		if User.objects.filter(email__iexact=email).exists():
# 			raise serializers.ValidationError("Email already exists.")

# 		return email

# 	def validate_password(self, value: str) -> str:
# 		validate_password_strength(value)
# 		return value

# 	def validate(self, attrs):
# 		if attrs["password"] != attrs["password_confirm"]:
# 			raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
# 		return attrs

# 	def create(self, validated_data):
# 		try:
# 			return create_user(
# 				email=validated_data["email"],
# 				password=validated_data["password"],
# 				first_name=validated_data.get("first_name", ""),
# 				last_name=validated_data.get("last_name", ""),
# 			)
# 		except DjangoValidationError as exc:
# 			raise serializers.ValidationError({"email": ["Email already exists."]}) from exc


# class LoginSerializer(serializers.Serializer):
# 	email = serializers.EmailField()
# 	password = serializers.CharField(write_only=True)

# 	def validate(self, attrs):
# 		email = attrs.get("email", "").lower()
# 		password = attrs.get("password", "")
# 		user = authenticate_user(email=email, password=password)
# 		if not user:
# 			raise serializers.ValidationError("Invalid credentials.")
# 		if not user.is_active:
# 			raise serializers.ValidationError("Invalid credentials.")

# 		tokens = issue_tokens(user)
# 		return {
# 			"user": user,
# 			"tokens": tokens,
# 		}


# class RefreshSerializer(serializers.Serializer):
# 	refresh = serializers.CharField()

# 	def validate(self, attrs):
# 		serializer = TokenRefreshSerializer(data=attrs)
# 		serializer.is_valid(raise_exception=True)
# 		return serializer.validated_data


# class LogoutSerializer(serializers.Serializer):
# 	refresh = serializers.CharField()

# 	def validate(self, attrs):
# 		if not attrs.get("refresh"):
# 			raise serializers.ValidationError("Refresh token is required.")
# 		return attrs


# class ProfileSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = User
# 		fields = ("id", "email", "first_name", "last_name", "is_active", "date_joined")

# class ChatSerializer(serializers.Serializer):
#     ssession_id = serializers.UUIDField(
# 		required=False,
# 		allow_null=True
# 	)
#     message = serializers.CharField()