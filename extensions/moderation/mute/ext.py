__all__ = ("Mute",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger


logger = get_logger()


class Mute(Extension):
    # ToDo: mute
    # ToDo: unmute
    # ToDo: tempmute (limited time)
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    Mute(bot=bot)
