__all__ = ("Ban",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils.essentials import get_logger


logger = get_logger()


class Ban(Extension):
    # ToDo: ban (limited and/or unlimited time)
    # ToDo: unban
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    Ban(bot=bot)
