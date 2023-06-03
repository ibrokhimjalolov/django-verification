import logging
from dataclasses import dataclass, asdict
from django.core.cache import cache as _cache


def get_cache():
    return _cache


@dataclass
class EmailVerification:
    email: str
    uuid: str
    code: str
    attempt: int
    verified: bool

    @classmethod
    def retrieve(cls, email, uuid):
        cache = get_cache()
        key = cls.get_key(email, uuid)
        data = cache.get(key)
        if data:
            return cls(**data)

    @classmethod
    def delete(cls, email, uuid):
        cache = get_cache()
        key = cls.get_key(email, uuid)
        cache.delete(key)

    def save_state(self, expire=None):
        cache = get_cache()
        key = self.get_key(self.email, self.uuid)
        cache.set(key, asdict(self), expire)
        logging.debug(f"EmailVerification.save_state: {self}")

    @classmethod
    def get_key(cls, email, uuid):
        return f"email_verification:{email}:{uuid}"


def get_email_verification(email, uuid):
    return EmailVerification.retrieve(email, uuid)


def delete_email_verification(email, uuid):
    EmailVerification.delete(email, uuid)
