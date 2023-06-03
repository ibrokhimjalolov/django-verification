from django.urls import path
from . import views

app_name = 'verification'

urlpatterns = [
    path(
        "EmailVerifyVerificationCode/",
        views.EmailVerifyVerificationCodeView.as_view(),
        name="EmailVerifyVerificationCode"
    ),
    path(
        "EmailSendVerificationCode/",
        views.EmailSendVerificationCodeView.as_view(),
        name="EmailSendVerificationCode"
    ),
]
