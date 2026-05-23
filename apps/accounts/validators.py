import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validate_email_address(value: str) -> None:
	validate_email(value)


def validate_password_strength(value: str) -> None:
	if len(value) < 8:
		raise ValidationError("Password must be at least 8 characters long.")
	if not re.search(r"[A-Z]", value):
		raise ValidationError("Password must include at least one uppercase letter.")
	if not re.search(r"[a-z]", value):
		raise ValidationError("Password must include at least one lowercase letter.")
	if not re.search(r"\d", value):
		raise ValidationError("Password must include at least one number.")

	validate_password(value)
