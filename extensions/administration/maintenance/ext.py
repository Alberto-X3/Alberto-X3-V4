__all__ = ("Maintenance",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils.essentials import get_logger


logger = get_logger()


class Maintenance(Extension):
    requires = {"lib": [], "ext": ["administration.roles"]}
    # ToDo: start
    # ToDo: stop


def setup(bot: PrefixedInjectedClient) -> None:
    Maintenance(bot=bot)
