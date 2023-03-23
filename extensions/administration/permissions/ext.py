__all__ = ("Permissions",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger


logger = get_logger()


class Permissions(Extension):
    requires = {"lib": [], "ext": ["administration.roles"]}
    # ToDo: manage/set
    # ToDo: view


def setup(bot: PrefixedInjectedClient) -> None:
    Permissions(bot=bot)
