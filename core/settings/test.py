from .base import *


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"{env.str('REDIS_URL', 'redis://localhost:6379/0')}",
        "KEY_PREFIX": "django_verificatgion_test"
    }
}


VERIFICATION_SERVICE = {
    "email": {
        "skip_sending": True,
        "code_length": 6,
        "attempt_limit": 3,
        "code_charset": "0123456789",
        "code_expiration": 60 * 60 * 2,  # in seconds (2 hours)
        "template_context": {
            "company": "Your Company",
        }
    },
    "phone": {
        "skip_sending": True,
        "code_length": 6,
        "attempt_limit": 3,
        "code_charset": "0123456789",
        "code_expiration": 60 * 60 * 2,  # in seconds (2 hours)
    }
}
