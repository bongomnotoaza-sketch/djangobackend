from django.core.exceptions import ValidationError

from .models import User
from .services import EncryptionService
from .verification_service import VerificationService


class UpdateInfoService:

    UPDATABLE_FIELDS = {
        "first_name",
        "last_name",
        "email",
        "phone",
        "date_of_birth",
        "country",
        "province",
        "city",
        "street",
        "current_activity",
    }

    ENCRYPTED_FIELDS = {
        "first_name",
        "last_name",
        "email",
        "phone",
        "date_of_birth",
        "country",
        "province",
        "city",
        "street",
        "current_activity",
    }

    def __init__(self):
        self.encryption = EncryptionService()
        self.verification_service = VerificationService()

    def update_info(self, user, **data):
        """
        Update permitted user information.

        Authorization and permission checks are intentionally
        handled outside this service for now.
        """

        if not data:
            raise ValidationError(
                "No information was provided for update."
            )

        # -----------------------------------------
        # 1. Check allowed fields
        # -----------------------------------------

        invalid_fields = (
            set(data.keys()) - self.UPDATABLE_FIELDS
        )

        if invalid_fields:
            raise ValidationError(
                "One or more fields cannot be updated."
            )

        update_fields = []

        # -----------------------------------------
        # 2. Handle email separately
        # -----------------------------------------

        if "email" in data:

            email = data["email"]

            if not email:
                raise ValidationError(
                    "Email cannot be empty."
                )

            # Encrypt the new email
            encrypted_email = self.encryption.encrypt(
                str(email)
            )

            user.email = encrypted_email

            # New email must be verified again
            user.email_verified = False

            update_fields.extend([
                "email",
                "email_verified",
            ])

        # -----------------------------------------
        # 3. Handle all other fields
        # -----------------------------------------

        for field, value in data.items():

            # Email was already handled above
            if field == "email":
                continue

            if value is None:
                raise ValidationError(
                    f"{field} cannot be empty."
                )

            if field in self.ENCRYPTED_FIELDS:
                value = self.encryption.encrypt(
                    str(value)
                )

            setattr(user, field, value)

            update_fields.append(field)

        # -----------------------------------------
        # 4. Save changes
        # -----------------------------------------

        user.save(
            update_fields=update_fields
        )

        # -----------------------------------------
        # 5. Send verification email for new email
        # -----------------------------------------

        if "email" in data:

            self.verification_service.send_verification_email(
                user
            )

        return user