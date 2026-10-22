from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


class PasswordResetService:

    def reset_password(
        self,
        username,
        temporary_password,
        new_password,
        confirm_password,
    ):
        # -----------------------------------------
        # 1. Find user
        # -----------------------------------------

        try:
            user = User.objects.get(
                username=username
            )

        except User.DoesNotExist:
            raise ValidationError(
                "Unable to reset password."
            )

        # -----------------------------------------
        # 2. Require verified email
        # -----------------------------------------

        if not user.email_verified:
            raise ValidationError(
                "Unable to reset password."
            )

        # -----------------------------------------
        # 3. Make sure a temporary password exists
        # -----------------------------------------

        if not user.temporary_password_hash:
            raise ValidationError(
                "Unable to reset password."
            )

        # -----------------------------------------
        # 4. Verify temporary password
        # -----------------------------------------

        if not check_password(
            temporary_password,
            user.temporary_password_hash,
        ):
            raise ValidationError(
                "Unable to reset password."
            )

        # -----------------------------------------
        # 5. Confirm new password
        # -----------------------------------------

        if new_password != confirm_password:
            raise ValidationError(
                "Unable to reset password."
            )

        # -----------------------------------------
        # 6. Validate new password using Django
        # -----------------------------------------

        try:
            validate_password(
                new_password,
                user=user,
            )

        except ValidationError:
            raise ValidationError(
                "Unable to reset password."
            )

        # -----------------------------------------
        # 7. Hash new password
        # -----------------------------------------

        user.password = make_password(
            new_password
        )

        # -----------------------------------------
        # 8. Invalidate temporary password
        # -----------------------------------------

        user.temporary_password_hash = None

        # -----------------------------------------
        # 9. Save
        # -----------------------------------------

        user.save(
            update_fields=[
                "password",
                "temporary_password_hash",
            ]
        )

        return True