__all__ = ("System",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger


logger = get_logger()


class System(Extension):
    # ToDo: restart
    # ToDo: shutdown
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    System(bot=bot)
