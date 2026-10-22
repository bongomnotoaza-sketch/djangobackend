import docker

from authentication.models import User
from .resolver import ContainerResolverService


class CreateContainerService:

    def __init__(self, user: User):
        self.user = user

        self.client = docker.from_env()

        self.container_name = (
            ContainerResolverService.ubuntu_container(user)
        )

        self.volume_name = (
            ContainerResolverService.filesystem_volume(user)
        )

        self.image_name = "logictree-ubuntu"

        self.network_name = (
            ContainerResolverService.network()
        )


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