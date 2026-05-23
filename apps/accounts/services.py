from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from utils.jwt import get_tokens_for_user

User = get_user_model()


def create_user(*, email: str, password: str, first_name: str = "", last_name: str = "") -> User:
	email = email.strip().lower()
	if User.objects.filter(email__iexact=email).exists():
		raise ValidationError("Email already exists.")

	try:
		with transaction.atomic():
			return User.objects.create_user(
				username=email,
				email=email,
				password=password,
				first_name=first_name,
				last_name=last_name,
			)
	except IntegrityError as exc:
		raise ValidationError("Email already exists.") from exc


def authenticate_user(*, email: str, password: str) -> User | None:
	return authenticate(username=email.strip().lower(), password=password)


def issue_tokens(user: User) -> dict[str, str]:
	return get_tokens_for_user(user)
