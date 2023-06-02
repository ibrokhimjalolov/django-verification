from django.urls import path
from . import views

app_name = 'verification'

urlpatterns = [
    path(
        "EmailSendCode/",
        views.EmailVerifyVerificationCodeView.as_view(),
        name="EmailSendCodeView"
    ),
    path(
        "EmailSendVerificationCode/",
        views.EmailSendVerificationCodeView.as_view(),
        name="EmailSendCode"
    ),
]
