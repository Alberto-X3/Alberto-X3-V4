__all__ = ("Sudo",)

from interactions.ext.prefixed_commands.command import prefixed_command
from interactions.ext.prefixed_commands.context import PrefixedContext
from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger


logger = get_logger()


class Sudo(Extension):
    @prefixed_command(name="sudo", aliases=["!!"])
    async def sudo(self, ctx: PrefixedContext):
        await ctx.reply("Hello There, I've got no functionality...")
        # ToDo: sudo (either a rerun of failed command or input command to execute directly)


def setup(bot: PrefixedInjectedClient) -> None:
    Sudo(bot=bot)
