from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

from utils.jwt import get_tokens_for_user

User = get_user_model()


def create_user(*, email: str, password: str, first_name: str = "", last_name: str = "") -> User:
	if User.objects.filter(email=email).exists():
		raise ValidationError("Email already in use.")

	user = User.objects.create_user(
		username=email,
		email=email,
		password=password,
		first_name=first_name,
		last_name=last_name,
	)
	return user


def authenticate_user(*, email: str, password: str) -> User | None:
	return authenticate(username=email, password=password)


def issue_tokens(user: User) -> dict[str, str]:
	return get_tokens_for_user(user)
