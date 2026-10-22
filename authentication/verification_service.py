import hashlib
import secrets
from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailVerificationToken
from .services import EncryptionService
from .username_service import UsernameService


class VerificationService:

    TOKEN_EXPIRY_MINUTES = 30

    def __init__(self):
        self.encryption = EncryptionService()
        self.username_service = UsernameService()

    def create_verification_token(self, user):

        # Generate a cryptographically secure random token
        raw_token = secrets.token_urlsafe(32)

        # Hash token before storing it
        token_hash = hashlib.sha256(
            raw_token.encode("utf-8")
        ).digest()

        expires_at = (
            timezone.now()
            + timedelta(minutes=self.TOKEN_EXPIRY_MINUTES)
        )

        verification_token = EmailVerificationToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        return raw_token, verification_token

    def send_verification_email(self, user):

        raw_token, verification_token = (
            self.create_verification_token(user)
        )

        # Decrypt email only when needed
        email = self.encryption.decrypt(user.email)

        verification_link = (
            "http://127.0.0.1:8000/auth/verify-email/"
            f"?token={raw_token}"
        )

        send_mail(
            subject="Verify your email address",

            message=(
                "Please verify your email address by clicking "
                "the following link:\n\n"
                f"{verification_link}\n\n"
                "This link expires in "
                f"{self.TOKEN_EXPIRY_MINUTES} minutes."
            ),

            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return verification_token

    def verify_email(self, raw_token):

        # -----------------------------------------
        # 1. Hash received token
        # -----------------------------------------

        token_hash = hashlib.sha256(
            raw_token.encode("utf-8")
        ).digest()

        # -----------------------------------------
        # 2. Find unused token
        # -----------------------------------------

        try:

            verification_token = (
                EmailVerificationToken.objects.get(
                    token_hash=token_hash,
                    used=False,
                )
            )

        except EmailVerificationToken.DoesNotExist:

            return False

        # -----------------------------------------
        # 3. Check expiration
        # -----------------------------------------

        if verification_token.expires_at < timezone.now():

            return False

        user = verification_token.user

        # -----------------------------------------
        # 4. Mark email as verified
        # -----------------------------------------

        user.email_verified = True

        user.save(
            update_fields=["email_verified"]
        )

        # -----------------------------------------
        # 5. Mark verification token as used
        # -----------------------------------------

        verification_token.used = True

        verification_token.save(
            update_fields=["used"]
        )

        # -----------------------------------------
        # 6. Send username email
        # -----------------------------------------

        if not user.username_email_sent:

            try:

                self.username_service.send_username_email(user)

            except Exception:

                # Email failed.
                #
                # The user remains verified.
                # username_email_sent remains False.
                #
                # This allows the username email
                # to be retried later.

                return True

            # -------------------------------------
            # 7. Email successfully sent
            # -------------------------------------

            user.username_email_sent = True

            user.save(
                update_fields=["username_email_sent"]
            )

        return True