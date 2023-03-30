__all__ = ("BanSettings",)


from typing import cast
from AlbertoX3.settings import Settings


class BanSettings(Settings):
    delete_message_seconds = cast(Settings, 604800)  # 1 week
