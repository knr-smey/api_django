from rest_framework.throttling import SimpleRateThrottle


class IPRateThrottle(SimpleRateThrottle):
	scope = None

	def get_cache_key(self, request, view):
		if self.scope is None:
			return None

		return self.cache_format % {
			"scope": self.scope,
			"ident": self.get_ident(request),
		}


class LoginRateThrottle(IPRateThrottle):
	scope = "login"


class RegisterRateThrottle(IPRateThrottle):
	scope = "register"


class RefreshRateThrottle(IPRateThrottle):
	scope = "refresh"


class BurstRateThrottle(SimpleRateThrottle):
	scope = "burst"

	def get_cache_key(self, request, view):
		if request.user and request.user.is_authenticated:
			ident = f"user:{request.user.pk}"
		else:
			ident = f"ip:{self.get_ident(request)}"

		return self.cache_format % {
			"scope": self.scope,
			"ident": ident,
		}
