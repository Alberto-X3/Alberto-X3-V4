__all__ = ("Roles",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger


logger = get_logger()


class Roles(Extension):
    # ToDo: manage/set
    # ToDo: view
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    Roles(bot=bot)
