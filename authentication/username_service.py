import secrets
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .services import EncryptionService


class UsernameService:

    def __init__(self):
        self.encryption_service = EncryptionService()

    def generate_username(self, first_name, last_name):
        User = get_user_model()

        first = "".join(
            character
            for character in first_name
            if character.isalpha()
        ).upper()

        last = "".join(
            character
            for character in last_name
            if character.isalpha()
        ).upper()

        first_part = first[:3].ljust(3, "X")
        last_part = last[:3].ljust(3, "X")

        while True:

            number = "".join(
                secrets.choice(string.digits)
                for _ in range(3)
            )

            username = f"{last_part}{first_part}{number}"

            if not User.objects.filter(
                username=username
            ).exists():

                return username

    def send_username_email(self, user):

        # Decrypt only when needed for email delivery
        first_name = self.encryption_service.decrypt(
            user.first_name
        )

        email = self.encryption_service.decrypt(
            user.email
        )

        send_mail(
            subject="Your Logictree username",

            message=(
                f"Hello {first_name},\n\n"
                f"Your Logictree username is:\n\n"
                f"{user.username}\n\n"
                f"You will use this username to log in "
                f"to your Logictree account.\n\n"
                f"Please keep it safe.\n\n"
                f"Logictree"
            ),

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[
                email
            ],

            fail_silently=False,
        )