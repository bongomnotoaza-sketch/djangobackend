
import asyncio
import os
import pty
import signal
import subprocess

from channels.generic.websocket import AsyncWebsocketConsumer


class TerminalConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        # Get username from the authenticated Django session
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.send(
                text_data="\r\n\x1b[31mAuthentication required.\x1b[0m\r\n"
            )
            await self.close()
            return

        username = user.username
        self.container_name = f"{username}-ubuntu"

        # Check that the container exists
        exists = await asyncio.to_thread(
            subprocess.run,
            [
                "docker",
                "inspect",
                self.container_name,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if exists.returncode != 0:
            await self.send(
                text_data="\r\n"
                "\x1b[31mTerminal container does not exist.\x1b[0m"
                "\r\n"
            )
            await self.close()
            return

        self.master_fd, self.slave_fd = pty.openpty()

        # Check whether container is running
        running = await asyncio.to_thread(
            subprocess.run,
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

        if running.stdout.strip() != "true":
            command = [
                "docker",
                "start",
                "-ai",
                self.container_name,
            ]
        else:
            command = [
                "docker",
                "exec",
                "-it",
                self.container_name,
                "/bin/bash",
            ]

        self.process = subprocess.Popen(
            command,
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            close_fds=True,
            preexec_fn=os.setsid,
        )

        os.close(self.slave_fd)
        self.slave_fd = None

        self.connection_active = True

        self.reader_task = asyncio.create_task(
            self.read_output()
        )

    async def read_output(self):
        loop = asyncio.get_running_loop()

        try:
            while self.connection_active:
                try:
                    data = await loop.run_in_executor(
                        None,
                        os.read,
                        self.master_fd,
                        4096,
                    )

                    if not data:
                        break

                    await self.send(bytes_data=data)

                except (BrokenPipeError, OSError):
                    break

        except Exception:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        if not hasattr(self, "master_fd"):
            return

        try:
            if text_data is not None:
                os.write(
                    self.master_fd,
                    text_data.encode(),
                )

            elif bytes_data is not None:
                os.write(
                    self.master_fd,
                    bytes_data,
                )

        except (BrokenPipeError, OSError):
            await self.close()

    async def disconnect(self, close_code):
        self.connection_active = False

        # Stop reader
        if hasattr(self, "reader_task"):
            self.reader_task.cancel()

            try:
                await self.reader_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass

        # Clean up terminal process
        if hasattr(self, "process"):
            try:
                os.killpg(
                    self.process.pid,
                    signal.SIGHUP,
                )

                self.process.terminate()
                self.process.wait(timeout=2)

            except (
                ProcessLookupError,
                OSError,
                subprocess.TimeoutExpired,
            ):
                try:
                    self.process.kill()
                    self.process.wait(timeout=1)
                except (
                    ProcessLookupError,
                    OSError,
                ):
                    pass

        # Close PTY
        if hasattr(self, "master_fd"):
            try:
                os.close(self.master_fd)
            except OSError:
                pass

