from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.BinaryField()
    date_of_birth = models.BinaryField()
    country = models.BinaryField()
    province = models.BinaryField(blank=True)
    city = models.BinaryField()
    street = models.BinaryField(blank=True)
    current_activity = models.BinaryField()

    first_name = models.BinaryField()
    last_name = models.BinaryField()
    email = models.BinaryField()
    
    role = models.CharField(
    max_length=20,
    choices=[
        ("student", "Student"),
        ("educator", "Educator"),
        ("admin", "Admin"),
    ],
    default="student",
)

    email_verified = models.BooleanField(default=False)
    username_email_sent = models.BooleanField(default=False)
    
    temporary_password_hash = models.CharField(
    max_length=128,
    blank=True,
    null=True,
)


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="email_verification_tokens",
    )

    token_hash = models.BinaryField()

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    used = models.BooleanField(default=False)