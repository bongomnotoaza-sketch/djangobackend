import docker

from authentication.models import User


class CreateVolumeService:

    def __init__(self, user: User):
        self.user = user
        self.volume_name = f"{user.username}-filesystem"

        self.client = docker.from_env()

    def create(self):
        volume = self.client.volumes.create(
            name=self.volume_name
        )

        return volume