__all__ = ("DB",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger


logger = get_logger()


class DB(Extension):
    # ToDo: clear cache
    # ToDo: statistics about saved objects etc
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    DB(bot=bot)
