
class VerificationUnprocessableEntity(Exception):
    """Unprocessable Entity"""

    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)
