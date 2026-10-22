from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from filesystem.start_container_service import StartContainerService


class LoginService:

    def __init__(self):
        pass

    def login_user(self, request, username, password):
        if not username:
            raise ValidationError("Username is required.")

        if not password:
            raise ValidationError("Password is required.")

        user = authenticate(
            request=request,
            username=username,
            password=password,
        )

        if user is None:
            raise ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise ValidationError(
                "This account is inactive."
            )

        # -----------------------------------------
        # Start the user's filesystem container
        # -----------------------------------------

        start_container_service = StartContainerService(user)
        start_container_service.start()

        # Django creates/rotates the session
        # and associates it with this user.
        login(request, user)

        return user