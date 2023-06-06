import random
from uuid import uuid4
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from .. import serializers
from ..exceptions import VerificationUnprocessableEntity
from ..settings import get_phone_settings
from ..utils import PhoneVerification
from ..senders import send_phone_verification_code


class PhoneSendVerificationCodeView(APIView):
    """
    Send verification code to email
    """

    errors = {
        "phone_not_found": "Phone not found",
        "phone_not_verified": "Phone not verified",
        "phone_cant_send": "Phone can't send",
    }

    @swagger_auto_schema(
        request_body=serializers.PhoneSendCodeSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Phone verification code sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                        ),
                        "phone": openapi.Schema(
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
        serializer = serializers.PhoneSendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data["uuid"] = uuid4()
        validated_data["code"] = self.generate_code()
        phone_settings = get_phone_settings()
        phone_verification = PhoneVerification(
            phone=validated_data["phone"],
            uuid=validated_data["uuid"],
            code=validated_data["code"],
            attempt=0,
            verified=False
        )
        try:
            if not phone_settings["skip_sending"]:
                send_phone_verification_code(phone_verification)
        except VerificationUnprocessableEntity as e:
            response = {
                "success": False,
                "error_code": e.code,
                "error_message": e.message,
            }
            return Response(response, status=status.HTTP_200_OK)
        phone_verification.save_state(expire=phone_settings["code_expiration"])
        response = {
            "success": True,
            "phone": str(validated_data["phone"]),
            "uuid": validated_data["uuid"],
        }
        return Response(response, status=status.HTTP_200_OK)

    def fail(self, code):
        raise VerificationUnprocessableEntity(self.errors[code], code=code)

    @staticmethod
    def generate_code():
        settings = get_phone_settings()
        return "".join(random.choices(
            settings["code_charset"],
            k=settings["code_length"]
        ))


class PhoneVerifyVerificationCodeView(APIView):
    """
    Send verification code to email
    """

    errors = {
        "phone_invalid_code": "Invalid code",
        "phone_not_found": "Phone not found",
        "phone_already_verified": "Phone already verified",
    }

    @swagger_auto_schema(
        request_body=serializers.PhoneVerifyCodeSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Phone verification code sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                        ),
                        "phone": openapi.Schema(
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
        serializer = serializers.PhoneVerifyCodeSerializer(data=request.data)
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
            "phone": str(serializer.validated_data["phone"]),
        }
        return Response(response, status=status.HTTP_200_OK)

    def verify_verification_code(self, validated_data, raise_exception=False):
        phone_settings = get_phone_settings()
        phone_verification = PhoneVerification.retrieve(validated_data["phone"], validated_data["uuid"])
        if not phone_verification:
            self.fail("phone_not_found")
        if phone_verification.verified:
            self.fail("phone_already_verified")
        if phone_verification.attempt >= phone_settings["attempt_limit"]:
            phone_verification.delete(phone_verification.phone, phone_verification.uuid)
            self.fail("phone_not_found")
        if phone_verification.code != validated_data["code"]:
            phone_verification.attempt += 1
            phone_verification.save_state()
            self.fail("phone_invalid_code")
        phone_verification.verified = True
        phone_verification.save_state()

    def fail(self, code):
        raise VerificationUnprocessableEntity(self.errors[code], code=code)
