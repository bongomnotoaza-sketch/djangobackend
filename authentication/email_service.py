from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class EmailService:

    @staticmethod
    def send(
        to,
        subject,
        text,
        html=None,
        from_email=None,
    ):
        from_email = from_email or settings.DEFAULT_FROM_EMAIL

        email = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=from_email,
            to=[to],
        )

        if html:
            email.attach_alternative(html, "text/html")

        email.send(fail_silently=False)

        return True