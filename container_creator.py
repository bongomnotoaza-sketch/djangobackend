import docker


class CreateContainerService:

    def __init__(self):
        self.container_name = "MNOLIB641-ubuntu"
        self.volume_name = "MNOLIB641-filesystem"

        self.image_name = "ubuntu:latest"
        self.network_name = "logictree"

        self.client = docker.from_env()

    def create(self):
        container = self.client.containers.create(
            image=self.image_name,

            name=self.container_name,

            command=["tail", "-f", "/dev/null"],

            volumes={
                self.volume_name: {
                    "bind": "/workspace",
                    "mode": "rw"
                }
            },

            network=self.network_name,

            mem_limit="200m",
            nano_cpus=500_000_000
        )

        container.start()

        return container