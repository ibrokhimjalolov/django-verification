from uuid import uuid4
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from .. import serializers
from ..settings import get_email_settings
from ..utils import get_email_verification, EmailVerification
from dataclasses import asdict


class VerificationUnprocessableEntity(Exception):
    """Unprocessable Entity"""

    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class EmailSendVerificationCodeView(APIView):
    """
    Send verification code to email
    """

    errors = {
        "email_not_found": "Email not found",
        "email_not_verified": "Email not verified",
        "email_cant_send": "Email can't send",
    }

    @swagger_auto_schema(
        request_body=serializers.EmailSendCodeSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Email verification code sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                        ),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING,
                        ),
                        "uuid": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Unique identifier",
                        ),
                    }
                )
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.EmailSendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data["uuid"] = uuid4()
        validated_data["code"] = "1234"
        try:
            self.send_email_verification_code(validated_data, raise_exception=True)
        except VerificationUnprocessableEntity as e:
            response = {
                "success": False,
                "error_code": e.code,
                "error_message": e.message,
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "success": True,
            "email": validated_data["email"],
            "uuid": validated_data["uuid"],
        }
        return Response(response, status=status.HTTP_200_OK)

    def send_email_verification_code(self, validated_data, raise_exception=False):
        email_settings = get_email_settings()
        email_verification = EmailVerification(
            email=validated_data["email"],
            uuid=validated_data["uuid"],
            code="1234",
            attempt=0,
            verified=False
        )

        c = {**asdict(email_verification), **email_settings["template_context"]}
        text_content = render_to_string('verification/email/template.txt', c)
        html_content = render_to_string('verification/email/template.html', c)
        email = EmailMultiAlternatives('Subject', text_content)
        email.attach_alternative(html_content, "text/html")
        email.to = [validated_data["email"]]
        email.send()

        email_settings = get_email_settings()
        email_verification.save_state(expire=email_settings["code_expiration"])

    def fail(self, code):
        raise VerificationUnprocessableEntity(self.errors[code], code=code)


class EmailVerifyVerificationCodeView(APIView):
    """
    Send verification code to email
    """

    errors = {
        "email_invalid_code": "Invalid code",
        "email_not_found": "Email not found",
    }

    @swagger_auto_schema(
        request_body=serializers.EmailVerifyCodeSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Email verification code sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                        ),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING,
                        ),
                        "uuid": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Unique identifier",
                        ),
                    }
                )
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.EmailVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.verify_verification_code(serializer.validated_data, raise_exception=True)
        except VerificationUnprocessableEntity as ex:
            response = {
                "success": False,
                "error_code": ex.code,
                "error_message": ex.message,
            }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            "success": True,
            "email": serializer.validated_data["email"],
        }
        return Response(response, status=status.HTTP_200_OK)

    def verify_verification_code(self, validated_data, raise_exception=False):
        email_settings = get_email_settings()
        email_verification = get_email_verification(validated_data["email"], validated_data["uuid"])
        if email_verification.attempt >= email_settings["attempt_limit"]:
            self.fail("email_not_found")
        if email_verification.code != validated_data["code"]:
            email_verification.attempt += 1
            email_verification.save_state()
            self.fail("email_invalid_code")
        email_verification.verified = True
        email_verification.save_state()

    def fail(self, code):
        raise VerificationUnprocessableEntity(self.errors[code], code=code)
