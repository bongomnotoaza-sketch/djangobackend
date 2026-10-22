import docker

from authentication.models import User


class CreateContainerService:

    def __init__(self, user: User):
        self.user = user

        self.container_name = f"{user.username}-files"
        self.volume_name = f"{user.username}-filesystem"

        self.image_name = "logictree-python"
        self.network_name = "logictree"

        self.client = docker.from_env()

    def create(self):
        container = self.client.containers.create(
            image=self.image_name,

            name=self.container_name,

            volumes={
                self.volume_name: {
                    "bind": "/workspace",
                    "mode": "rw"
                }
            },

            network=self.network_name,

            restart_policy={
                "Name": "unless-stopped"
            }
        )

        container.start()

        return container