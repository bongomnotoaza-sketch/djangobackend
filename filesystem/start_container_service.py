import docker

from authentication.models import User


class StartContainerService:

    def __init__(self, user: User):
        self.user = user
        self.container_name = f"{user.username}-files"

        self.client = docker.from_env()

    def start(self):
        container = self.client.containers.get(
            self.container_name
        )

        container.start()

        return container