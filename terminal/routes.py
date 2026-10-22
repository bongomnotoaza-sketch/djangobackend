
from django.urls import re_path

from .consumers import TerminalConsumer


websocket_urlpatterns = [
    re_path(
        r"^terminal/$",
        TerminalConsumer.as_asgi(),
    ),
]

