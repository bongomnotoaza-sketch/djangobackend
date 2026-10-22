import asyncio
import os
import pty
import signal
import subprocess

from authorization.authorization_service import AuthorizationService
from docker_manager.services.resolver import ContainerResolverService


class DockerTerminal:

    def __init__(self, request):

        auth = AuthorizationService.authorize(request)

        if not auth["authenticated"]:
            raise Exception(
                "User not authenticated"
            )

        self.user = auth["user"]

        self.container_name = (
            ContainerResolverService
            .ubuntu_container(self.user)
        )

        self.master_fd = None
        self.process = None


    def container_exists(self):

        result = subprocess.run(
            [
                "docker",
                "inspect",
                self.container_name,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return result.returncode == 0


    def container_running(self):

        result = subprocess.run(
            [
                "docker",
                "inspect",
                "-f",
                "{{.State.Running}}",
                self.container_name,
            ],
            capture_output=True,
            text=True,
        )

        return result.stdout.strip() == "true"


    def start_container(self):

        if not self.container_exists():
            raise Exception(
                "Container does not exist"
            )

        if not self.container_running():

            subprocess.run(
                [
                    "docker",
                    "start",
                    self.container_name,
                ],
                check=True,
            )


    def start_shell(self):

        self.start_container()

        self.master_fd, slave_fd = pty.openpty()

        self.process = subprocess.Popen(
            [
                "docker",
                "exec",
                "-i",
                "-t",
                self.container_name,
                "/bin/bash",
            ],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            preexec_fn=os.setsid,
        )

        os.close(slave_fd)


    async def read_output(self, websocket):

        loop = asyncio.get_running_loop()

        while True:

            try:

                data = await loop.run_in_executor(
                    None,
                    os.read,
                    self.master_fd,
                    4096,
                )

                if not data:
                    break

                await websocket.send(
                    bytes_data=data
                )

            except (
                OSError,
                BrokenPipeError
            ):
                break


    def write_input(self, data):

        try:

            os.write(
                self.master_fd,
                data
            )

        except (
            OSError,
            BrokenPipeError
        ):
            pass


    def stop(self):

        if self.master_fd:

            try:
                os.close(
                    self.master_fd
                )

            except OSError:
                pass


        if self.process:

            try:

                os.killpg(
                    self.process.pid,
                    signal.SIGHUP
                )

            except (
                ProcessLookupError,
                OSError
            ):
                pass