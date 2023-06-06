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
        logging.debug(f"{self.__class__.__name__}.save_state: {self}")

    @classmethod
    def get_key(cls, email, uuid):
        return f"email_verification:{email}:{uuid}"


@dataclass
class PhoneVerification:
    phone: str
    uuid: str
    code: str
    attempt: int
    verified: bool

    @classmethod
    def retrieve(cls, phone, uuid):
        cache = get_cache()
        key = cls.get_key(phone, uuid)
        data = cache.get(key)
        if data:
            return cls(**data)

    @classmethod
    def delete(cls, phone, uuid):
        cache = get_cache()
        key = cls.get_key(phone, uuid)
        cache.delete(key)

    def save_state(self, expire=None):
        cache = get_cache()
        key = self.get_key(self.phone, self.uuid)
        cache.set(key, asdict(self), expire)
        logging.debug(f"{self.__class__.__name__}.save_state: {self}")

    @classmethod
    def get_key(cls, phone, uuid):
        return f"phone_verification:{phone}:{uuid}"
