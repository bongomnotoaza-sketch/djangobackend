from django.contrib.auth import logout
from filesystem.stop_container_service import StopContainerService


class LogoutService:

    def __init__(self):
        self.stop_container_service = StopContainerService()

    def logout_user(self, request):
        """
        Log out the currently authenticated user
        and invalidate their Django session.
        """

        # Get the user before logging out
        user = request.user

        # -----------------------------------------
        # Stop the user's filesystem container
        # -----------------------------------------

        if user.is_authenticated:
            self.stop_container_service.stop_container(
                user.username
            )

        # Django invalidates the session
        logout(request)

        return True