from django.test import TestCase
from django.urls import reverse_lazy

from apps.verification.settings import get_email_settings
from apps.verification.utils import EmailVerification, PhoneVerification


class PhoneTest(TestCase):

    def test_invalid_email(self):
        phone = "fake"  # invalid format of phone number
        response = self.client.post(reverse_lazy("verification:PhoneSendVerificationCode"), {"phone": phone})
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.data, dict)

    def test_attempt_limit(self):
        phone = "+998990001122"
        data = self.send_code(phone)
        uuid = data["uuid"]
        email_settings = get_email_settings()

        wrong_code = "XXX"
        for attempt in range(email_settings["attempt_limit"]):
            response = self.check_code(phone, uuid, wrong_code)
            self.assertFalse(response["success"])
            self.assertEqual(response["error_code"], "phone_invalid_code")

        response = self.check_code(phone, uuid, wrong_code)
        self.assertFalse(response["success"])
        self.assertEqual(response["error_code"], "phone_not_found")

    def test_correct_code(self):
        phone = "+998990001122"
        data = self.send_code(phone)
        uuid = data["uuid"]
        correct_code = PhoneVerification.retrieve(phone, uuid).code
        response = self.check_code(phone, uuid, correct_code)
        self.assertTrue(response["success"])

    def send_code(self, phone):
        response = self.client.post(reverse_lazy("verification:PhoneSendVerificationCode"), {"phone": phone})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertTrue(response.data["success"])
        return response.data

    def check_code(self, phone, uuid, code):
        response = self.client.post(
            reverse_lazy("verification:PhoneVerifyVerificationCode"),
            {"phone": phone, "uuid": uuid, "code": code},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        return response.data
