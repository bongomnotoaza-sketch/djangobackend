from django.core.exceptions import ObjectDoesNotExist

from .models import User


class AccountService:

    @staticmethod
    def deactivate_user(user_id):
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            raise ValueError("User does not exist.")

        user.is_active = False
        user.save(update_fields=["is_active"])

        return user

    @staticmethod
    def activate_user(user_id):
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            raise ValueError("User does not exist.")

        user.is_active = True
        user.save(update_fields=["is_active"])

        return user