from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import User


class RegistrationValidator:

    @staticmethod
    def validate_username(username):
        if not username:
            raise ValidationError("Username is required.")

        if User.objects.filter(username=username).exists():
            raise ValidationError("Username is already taken.")

        return username

    @staticmethod
    def validate_password(password, user=None):
        if not password:
            raise ValidationError("Password is required.")

        password_validation.validate_password(
            password,
            user=user
        )

        return password

    @staticmethod
    def validate_email(email):
        if not email:
            raise ValidationError("Email is required.")

        validate_email(email)

        return email

    @staticmethod
    def validate_required_fields(data):
        required_fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "country",
            "city",
            "current_activity",
        ]

        missing_fields = [
            field
            for field in required_fields
            if not data.get(field)
        ]

        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        return True

    @classmethod
    def validate_registration(cls, data):
        cls.validate_required_fields(data)

        cls.validate_username(
            data["username"]
        )

        cls.validate_password(
            data["password"]
        )

        cls.validate_email(
            data["email"]
        )

        return True