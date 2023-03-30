__all__ = ("Sudo",)


from interactions.api.events.base import RawGatewayEvent
from interactions.api.events.internal import CommandCompletion
from interactions.ext.prefixed_commands.command import PrefixedCommand, prefixed_command
from interactions.ext.prefixed_commands.context import PrefixedContext
from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient
from interactions.models.discord.channel import BaseChannel
from interactions.models.internal.application_commands import SlashCommand
from interactions.models.internal.command import check
from interactions.models.internal.context import BaseContext
from interactions.models.internal.listener import listen

from AlbertoX3.constants import Config
from AlbertoX3.environment import OWNER_ID
from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.permission import permission_override
from AlbertoX3.utils.essentials import get_logger


logger = get_logger()


@check
async def is_super_user(ctx: BaseContext) -> bool:
    if ctx.author.id != OWNER_ID:
        return False
    return True


class Sudo(Extension):
    enabled = True
    requires = {"lib": [], "ext": []}

    cmd_cache: dict[BaseChannel, tuple[PrefixedCommand | SlashCommand, list, dict]]

    def __init__(self, *_: ..., **__: ...):
        self.cmd_cache = {}

    @listen()
    async def on_owner_cmd(self, event: CommandCompletion):
        if (ctx := event.ctx).author.id == OWNER_ID:
            if isinstance(cmd := ctx.command, (PrefixedCommand, SlashCommand)):
                if cmd.name != self.sudo.name:  # type: ignore
                    self.cmd_cache[ctx.channel] = (cmd, ctx.args, ctx.kwargs)  # type: ignore

    @prefixed_command(name="sudo", aliases=["!!"])
    @is_super_user
    async def sudo(self, ctx: PrefixedContext, *, command: str = ""):
        permission_override.set(Config.PERMISSION_LEVELS.max())

        if command:  # could also just use ctx.content_parameters
            event = RawGatewayEvent()
            event.data["content"] = "dummy content, isn't used at all..."
            event.data["guild_id"] = ctx.guild_id
            event.data["channel_id"] = ctx.channel_id
            event.data["id"] = ctx.message_id
            event.data["webhook"] = False
            event.data["author"] = {"bot": False}

            orig_content = ctx.message.content
            base_data = {"channel_id": event.data["channel_id"], "id": event.data["id"]}

            # manipulate message content in cache
            self.bot.cache.place_message_data(base_data | {"content": ctx.prefix + ctx.content_parameters})
            try:
                # process new command
                await self.bot.prefixed._dispatch_prefixed_commands(event)  # noqa
            finally:
                # correct message content in cache (if it wasn't deleted in the meantime)
                if self.bot.cache.get_message(base_data["channel_id"], base_data["id"]) is not None:
                    self.bot.cache.place_message_data(base_data | {"content": orig_content})

        else:
            ctx.command, ctx.args, ctx.kwargs = self.cmd_cache.get(ctx.channel, (None, (), {}))
            if (cmd := ctx.command) is None:
                # no commands have been run in the current channel
                return

            if isinstance(cmd, PrefixedCommand):
                # let's reverse the data processing and recreate the war event \o/
                pass
                # event: RawGatewayEvent
                # await self.bot.prefixed._dispatch_prefixed_commands(event)  # noqa

            if isinstance(cmd, SlashCommand):
                # let's create a new context with faked endpoints \o/
                pass
                # await self.bot._run_slash_command(command=ctx.command, ctx=ctx)  # noqa


def setup(bot: PrefixedInjectedClient) -> None:
    Sudo(bot=bot)
