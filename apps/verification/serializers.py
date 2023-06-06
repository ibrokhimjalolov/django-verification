from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


class EmailSendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=512, required=True)


class EmailVerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=512, required=True)
    uuid = serializers.UUIDField(required=True)
    code = serializers.CharField(max_length=16, required=True)


class PhoneSendCodeSerializer(serializers.Serializer):
    phone = PhoneNumberField()


class PhoneVerifyCodeSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    uuid = serializers.UUIDField(required=True)
    code = serializers.CharField(max_length=16, required=True)
