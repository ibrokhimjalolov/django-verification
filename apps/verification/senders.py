from dataclasses import asdict

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .exceptions import VerificationUnprocessableEntity
from .utils import EmailVerification, PhoneVerification


def send_email_verification_code(email_verification: EmailVerification, template_context, raise_exception=False):
    template_txt = "verification/email/template.txt"
    template_html = "verification/email/template.html"
    template_context = {**asdict(email_verification), **template_context}
    text_content = render_to_string(template_txt, template_context)
    html_content = render_to_string(template_html, template_context)
    email = EmailMultiAlternatives('Subject', text_content)
    email.attach_alternative(html_content, "text/html")
    email.to = [email_verification.email]
    try:
        email.send()
    except Exception as ex:
        raise VerificationUnprocessableEntity(
            message="Email can't send %s" % str(ex), code="email_cant_send"
        )


def send_phone_verification_code(phone_verification: PhoneVerification, raise_exception=False):
    print("Sending...", phone_verification)
