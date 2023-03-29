__all__ = ("Language",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils.essentials import get_logger


logger = get_logger()


class Language(Extension):
    # ToDo: set (change language for bot responses)
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    Language(bot=bot)
