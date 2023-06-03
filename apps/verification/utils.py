from dataclasses import dataclass


def check_email_for_code(email, uuid, code):
    """

    """
    print("check_email_for_code", email, uuid, code)
    return True


@dataclass
class EmailVerification:
    email: str
    uuid: str
    code: str
    attempt: int
    verified: bool

    def save_state(self, expire=None):
        print("Saving", self)
    

def get_email_verification(email, uuid):
    return EmailVerification(email, uuid, "1234", 0, False)


def delete_email_verification(email, uuid):
    pass
