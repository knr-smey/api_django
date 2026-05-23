from apps.accounts.security import track_suspicious_ip


class SuspiciousRequestMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if request.path.startswith("/api/"):
			track_suspicious_ip(request)

		return self.get_response(request)
