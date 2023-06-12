from django.test import TestCase
from django.urls import reverse_lazy
from django.core.cache import cache
from apps.verification.settings import get_email_settings
from apps.verification.utils import EmailVerification


class EmailTest(TestCase):

    def setUp(self) -> None:
        cache.clear()

    def test_invalid_email(self):
        email = "fake"  # invalid format of phone number
        response = self.client.post(reverse_lazy("verification:EmailSendVerificationCode"), {"email": email})
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.data, dict)

    def test_attempt_limit(self):
        email = "fake@fake.org"
        data = self.send_code(email)
        uuid = data["uuid"]
        email_settings = get_email_settings()

        wrong_code = "XXX"
        for attempt in range(email_settings["attempt_limit"]):
            response = self.check_code(email, uuid, wrong_code)
            self.assertFalse(response["success"])
            self.assertEqual(response["error_code"], "email_invalid_code")

        response = self.check_code(email, uuid, wrong_code)
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "email_not_found")

    def test_correct_code(self):
        email = "fake@fake.com"
        data = self.send_code(email)
        uuid = data["uuid"]
        correct_code = EmailVerification.retrieve(email, uuid).code
        response = self.check_code(email, uuid, correct_code)
        self.assertTrue(response["success"])

    def send_code(self, email):
        response = self.client.post(reverse_lazy("verification:EmailSendVerificationCode"), {"email": email})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertTrue(response.data["success"])
        return response.data

    def check_code(self, email, uuid, code):
        response = self.client.post(
            reverse_lazy("verification:EmailVerifyVerificationCode"),
            {"email": email, "uuid": uuid, "code": code},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        return response.data
