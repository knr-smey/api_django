from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message: str = "Success", status_code: int = status.HTTP_200_OK):
	payload = {"success": True, "message": message, "data": data}
	return Response(payload, status=status_code)


def error_response(
	message: str = "Error",
	errors=None,
	status_code: int = status.HTTP_400_BAD_REQUEST,
):
	payload = {"success": False, "message": message, "errors": errors}
	return Response(payload, status=status_code)
