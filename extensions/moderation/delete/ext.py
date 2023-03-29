__all__ = ("Delete",)


from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils.essentials import get_logger


logger = get_logger()


class Delete(Extension):
    # ToDo: delete (amount (in general or by-user), until (e.g. last hour))
    pass


def setup(bot: PrefixedInjectedClient) -> None:
    Delete(bot=bot)
