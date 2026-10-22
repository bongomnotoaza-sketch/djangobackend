import secrets
import string

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

from .models import User
from .services import EncryptionService
from .email_service import EmailService


class PasswordRecoveryService:

    TEMP_PASSWORD_LENGTH = 16

    RESET_PASSWORD_URL = (
        "https://www.logictree.co.za/auth/password_reset_page/"
    )

    def __init__(self):
        self.encryption = EncryptionService()

    def get_user(self, username):
        try:
            user = User.objects.get(
                username=username
            )

        except User.DoesNotExist:
            raise ValidationError(
                "Unable to process password recovery request."
            )

        if not user.email_verified:
            raise ValidationError(
                "Unable to process password recovery request."
            )

        return user

    def generate_temporary_password(self, user):
        characters = (
            string.ascii_letters
            + string.digits
            + "!@#$%^&*"
        )

        temporary_password = "".join(
            secrets.choice(characters)
            for _ in range(self.TEMP_PASSWORD_LENGTH)
        )

        user.temporary_password_hash = make_password(
            temporary_password
        )

        user.save(
            update_fields=["temporary_password_hash"]
        )

        return temporary_password

    def send_password_recovery_email(self, user):

        if not user.email_verified:
            raise ValidationError(
                "Unable to process password recovery request."
            )

        temporary_password = (
            self.generate_temporary_password(user)
        )

        email = self.encryption.decrypt(
            user.email
        )

        EmailService.send(
            to=email,
            subject="Logictree password recovery",
            text=(
                "We received a request to reset your "
                "Logictree password.\n\n"

                "Your temporary password is:\n\n"
                f"{temporary_password}\n\n"

                "Use this temporary password together "
                "with your username to create a new password.\n\n"

                "Password reset page:\n"
                f"{self.RESET_PASSWORD_URL}\n\n"

                "If you did not request a password reset, "
                "you can safely ignore this email."
            ),
        )

        return True