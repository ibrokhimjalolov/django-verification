from rest_framework import serializers


class EmailSendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=512, required=True)


class EmailVerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=512, required=True)
    uuid = serializers.UUIDField(required=True)
    code = serializers.CharField(max_length=16, required=True)
