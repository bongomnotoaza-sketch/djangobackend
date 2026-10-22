import docker


class StopContainerService:

    def __init__(self):
        self.client = docker.from_env()

    def stop_container(self, username: str):
        container_name = f"{username}-files"

        container = self.client.containers.get(container_name)

        container.stop()

        return container