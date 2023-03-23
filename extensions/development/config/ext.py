__all__ = ("Config",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger


logger = get_logger()


class Config(Extension):
    # ToDo: manage/set/change
    # ToDo: view
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    Config(bot=bot)
