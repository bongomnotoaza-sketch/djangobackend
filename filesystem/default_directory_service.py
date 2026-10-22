from authentication.models import User

from .main_service import MainService
from .start_container_service import StartContainerService
from .stop_container_service import StopContainerService


class DefaultDirectoryService:

    def __init__(self, user: User):
        self.user = user

        self.main_service = MainService()

        self.start_container_service = StartContainerService(
            user
        )

        self.stop_container_service = StopContainerService()

    def create_default_directories(self):

        # -----------------------------------------
        # 1. Start filesystem container
        # -----------------------------------------

        self.start_container_service.start()

        try:

            # -----------------------------------------
            # 2. Default directories
            # -----------------------------------------

            directories = [
                "Home",
                "Desktop",
                "Documents",
                "Downloads",
                "Public",
                "Templates",
            ]

            results = []

            # -----------------------------------------
            # 3. Create Home
            # -----------------------------------------

            home_result = self.main_service.create_folder(
                username=self.user.username,
                name="Home",
                path=""
            )

            results.append({
                "name": "Home",
                "result": home_result
            })

            # -----------------------------------------
            # 4. Create directories inside Home
            # -----------------------------------------

            for directory in directories[1:]:

                result = self.main_service.create_folder(
                    username=self.user.username,
                    name=directory,
                    path="Home"
                )

                results.append({
                    "name": directory,
                    "result": result
                })

            return results

        finally:

            # -----------------------------------------
            # 5. Stop filesystem container
            # -----------------------------------------

            self.stop_container_service.stop_container(
                self.user.username
            )