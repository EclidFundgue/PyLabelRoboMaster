from typing import Any

from ..pygame_gui import BaseComponent


class MessagePrint(BaseComponent):
    def onReceive(self, sender_id: int, theme: str, message: Any) -> None:
        print(f'({sender_id})[{theme}: {message}]')