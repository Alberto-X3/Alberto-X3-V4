__all__ = ("Kick",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils.essentials import get_logger


logger = get_logger()


class Kick(Extension):
    # ToDo: kick
    # ToDo: hardkick (deletes messages (basically ban with immediate unban)
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    Kick(bot=bot)
