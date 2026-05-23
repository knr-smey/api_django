import logging

from rest_framework import status
from rest_framework.views import exception_handler

from apps.accounts.security import get_client_ip

logger = logging.getLogger("security")


def custom_exception_handler(exc, context):
	response = exception_handler(exc, context)
	if response is None:
		return response

	if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
		request = context.get("request")
		if request is not None:
			logger.warning(
				"Rate limit exceeded",
				extra={
					"ip_address": get_client_ip(request),
					"path": request.path,
					"method": request.method,
				},
			)
		response.data = {
			"success": False,
			"message": "Too many requests. Please try again later.",
		}
		return response

	if response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}:
		response.data = {
			"success": False,
			"message": "Authentication credentials were not provided or are invalid.",
		}

	return response
