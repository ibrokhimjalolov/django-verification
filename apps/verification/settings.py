from django.conf import settings


SETTINGS_NAME = "VERIFICATION_SERVICE"


def get_email_settings() -> dict:
    default_settings = {
        "skip_sending": True,
        "code_length": 6,
        "attempt_limit": 3,
        "code_charset": "0123456789",
        "code_expiration": 60 * 60 * 2,  # in seconds (2 hours)
        "template_context": {
            "company": "Your Company",
        }
    }
    project_settings = getattr(settings, SETTINGS_NAME, {}).get("email", {})
    return {
        **default_settings,
        **project_settings
    }


def get_phone_settings() -> dict:
    default_settings = {
        "skip_sending": True,
        "code_length": 6,
        "attempt_limit": 3,
        "code_charset": "0123456789",
        "code_expiration": 60 * 60 * 2,  # in seconds (2 hours)
    }
    project_settings = getattr(settings, SETTINGS_NAME, {}).get("phone", {})
    return {
        **default_settings,
        **project_settings
    }
