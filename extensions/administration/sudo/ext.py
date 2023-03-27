__all__ = ("Sudo",)

from interactions.ext.prefixed_commands.command import prefixed_command
from interactions.ext.prefixed_commands.context import PrefixedContext
from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger, get_extensions


logger = get_logger()


class Sudo(Extension):
    enabled = True
    requires = {"lib": [], "ext": []}

    @prefixed_command(name="sudo", aliases=["!!"])
    async def sudo(self, ctx: PrefixedContext):
        from pathlib import Path
        from AlbertoX3.aio import run_in_thread
        from AlbertoX3.utils import get_installed_libraries

        await ctx.reply("Hello There, I've got no functionality...")
        await ctx.reply(
            "```\n" + "\n".join([ext.full_name for ext in get_extensions(folder=Path("./extensions/"))]) + "\n```"
        )
        await ctx.reply(f"``{await run_in_thread(get_installed_libraries)}``")
        # ToDo: sudo (either a rerun of failed command or input command to execute directly)


def setup(bot: PrefixedInjectedClient) -> None:
    Sudo(bot=bot)
