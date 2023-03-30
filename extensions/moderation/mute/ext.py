__all__ = ("Mute",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils.essentials import get_logger


logger = get_logger()


class Mute(Extension):
    # ToDo: mute (unlimited / limited time)
    # ToDo: unmute
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    Mute(bot=bot)
