import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer

from authorization.authorization_service import AuthorizationService
from .services.terminal import DockerTerminal


class TerminalConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        auth = AuthorizationService.authorize(
            self.scope
        )

        if not auth["authenticated"]:
            await self.close()
            return


        await self.accept()


        self.terminal = DockerTerminal(
            self.scope
        )


        try:

            self.terminal.start_shell()


        except Exception as e:

            await self.send(
                text_data=f"Terminal error: {str(e)}"
            )

            await self.close()
            return


        self.reader_task = asyncio.create_task(
            self.terminal.read_output(self)
        )


    async def receive(
        self,
        text_data=None,
        bytes_data=None
    ):

        if text_data is not None:

            self.terminal.write_input(
                text_data.encode()
            )


        elif bytes_data is not None:

            self.terminal.write_input(
                bytes_data
            )


    async def disconnect(self, close_code):

        if hasattr(self, "reader_task"):

            self.reader_task.cancel()


        if hasattr(self, "terminal"):

            self.terminal.stop()