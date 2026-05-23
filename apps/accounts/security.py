import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger("security")


FAILED_LOGIN_LIMIT = getattr(settings, "FAILED_LOGIN_LIMIT", 5)
FAILED_LOGIN_WINDOW = getattr(settings, "FAILED_LOGIN_WINDOW", 15 * 60)
SUSPICIOUS_IP_THRESHOLD = getattr(settings, "SUSPICIOUS_IP_THRESHOLD", 20)
SUSPICIOUS_IP_WINDOW = getattr(settings, "SUSPICIOUS_IP_WINDOW", 10 * 60)


def get_client_ip(request) -> str:
	forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
	if forwarded_for:
		return forwarded_for.split(",")[0].strip()
	return request.META.get("REMOTE_ADDR", "")


def _failed_login_key(ip_address: str, email: str) -> str:
	return f"auth:failed-login:{ip_address}:{email.lower()}"


def is_login_blocked(ip_address: str, email: str) -> bool:
	return int(cache.get(_failed_login_key(ip_address, email), 0)) >= FAILED_LOGIN_LIMIT


def record_failed_login(ip_address: str, email: str) -> int:
	key = _failed_login_key(ip_address, email)
	attempts = cache.get(key)
	if attempts is None:
		cache.set(key, 1, FAILED_LOGIN_WINDOW)
		attempts = 1
	else:
		try:
			attempts = cache.incr(key)
		except ValueError:
			cache.set(key, 1, FAILED_LOGIN_WINDOW)
			attempts = 1

	if attempts >= FAILED_LOGIN_LIMIT:
		logger.warning(
			"Login temporarily blocked after repeated failures",
			extra={"ip_address": ip_address, "email": email.lower(), "attempts": attempts},
		)

	return attempts


def clear_failed_login(ip_address: str, email: str) -> None:
	cache.delete(_failed_login_key(ip_address, email))


def track_suspicious_ip(request) -> None:
	ip_address = get_client_ip(request)
	if not ip_address:
		return

	key = f"security:requests:{ip_address}"
	requests = cache.get(key)
	if requests is None:
		cache.set(key, 1, SUSPICIOUS_IP_WINDOW)
		return

	try:
		requests = cache.incr(key)
	except ValueError:
		cache.set(key, 1, SUSPICIOUS_IP_WINDOW)
		return

	if requests == SUSPICIOUS_IP_THRESHOLD:
		logger.warning(
			"Suspicious request volume detected",
			extra={
				"ip_address": ip_address,
				"path": request.path,
				"method": request.method,
				"requests": requests,
			},
		)
