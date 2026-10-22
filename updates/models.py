from django.db import models
from authentication.models import User


class Updates(models.Model):
    id = models.BigAutoField(primary_key=True)

    initials = models.CharField(max_length=20)
    heading = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    senddate = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100)
    body = models.TextField()

    def __str__(self):
        return self.heading


class Read(models.Model):
    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="read_updates",
    )

    update = models.ForeignKey(
        Updates,
        on_delete=models.CASCADE,
        related_name="read_by",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "update"],
                name="unique_user_update_read",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.update}"