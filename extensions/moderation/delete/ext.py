__all__ = ("Delete",)


from datetime import datetime, timedelta
from typing import cast

from interactions.client.errors import HTTPException
from interactions.ext.prefixed_commands.command import prefixed_command
from interactions.ext.prefixed_commands.context import PrefixedContext
from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient
from interactions.models.discord.message import Message
from interactions.models.discord.snowflake import Snowflake
from interactions.models.discord.user import User, Member
from interactions.models.internal.checks import guild_only
from interactions.models.internal.command import check
from interactions.models.internal.listener import listen
from interactions.models.internal.tasks.task import Task
from interactions.models.internal.tasks.triggers import IntervalTrigger, DateTrigger

from AlbertoX3.constants import Config
from AlbertoX3.converters import DurationConverter, IntConverter
from AlbertoX3.errors import InternalNotImplementedError
from AlbertoX3.database import db, filter_by
from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.translations import TranslationNamespace, t  # type: ignore
from AlbertoX3.utils.essentials import get_logger
from AlbertoX3.utils.general import get_utcnow
from AlbertoX3.utils.ipy import get_embed

from .colors import Colors
from .permission import DeletePermission


logger = get_logger()
tg: TranslationNamespace = cast(TranslationNamespace, t.g)
t: TranslationNamespace = cast(TranslationNamespace, t.delete)

MAX_MESSAGES_AT_A_TIME: int = 100  # to prevent abuse with a super long delete


class Delete(Extension):
    enabled = True
    requires = {"lib": [], "ext": []}

    @prefixed_command(name="delete", aliases=["del"])
    @DeletePermission.delete.check
    async def delete(
        self,
        ctx: PrefixedContext,
        amount: IntConverter.with_range(min=0, max=MAX_MESSAGES_AT_A_TIME) = 0,
        mode: User | Message | DurationConverter = None,
    ) -> None:
        # valid configurations:
        #   A: amount > 0 --> delete N messages
        #   B: amount > 0 and <type>mode == User --> delete N message from user
        #   C: <type>mode == Message --> delete specified message
        #   D: <type>mode == timedelta --> delete all message in the past interval
        print(amount, mode, sep="\n")  # ToDo: remove in future
        reason = f"Initiated by {ctx.author.tag}"
        title = t.delete.success.title
        color = Colors.delete

        if amount > 0:
            if isinstance(mode, User):  # B
                amount += ctx.author_id == mode.id
                count = await ctx.channel.purge(
                    deletion_limit=amount,
                    search_limit=0,
                    avoid_loading_msg=False,
                    predicate=lambda m: m.author.id == mode.id,
                    reason=reason,
                )
                description = t.delete.success.info.b(count=count, channel=ctx.channel.mention, user=f"<@{mode.id}>")

            else:  # A
                amount += 1  # the author send a message as well
                count = await ctx.channel.purge(
                    deletion_limit=amount,
                    search_limit=0,
                    avoid_loading_msg=Config.MESSAGES_AVOID_LOADING_MSG,
                    reason=reason,
                )
                description = t.delete.success.info.a(count=count, channel=ctx.channel.mention)

        elif isinstance(mode, Message):  # C
            # don't just delete, user may have no rights in the message's context
            description = t.delete.success.info.c
            description += "\n\n**:warning: THIS CONFIGURATION IS DISABLED ATM**"
            # disabled sound way better than "not implemented" ^^

        elif isinstance(mode, timedelta):  # D
            border_timestamp = Snowflake.from_datetime(get_utcnow() - abs(mode))
            limit = MAX_MESSAGES_AT_A_TIME + 1  # the author send a message as well
            count = await ctx.channel.purge(
                deletion_limit=limit,
                search_limit=limit,
                avoid_loading_msg=False,
                predicate=lambda m: m.id > border_timestamp,
                reason=reason,
            )
            description = t.delete.success.info.d(
                count=count,
                channel=ctx.channel.mention,
                timestamp=int(border_timestamp.created_at.timestamp()),
                now=int(get_utcnow().timestamp()),
            )

        elif mode is not None:
            raise InternalNotImplementedError(f"Delete for {type(mode)!r}")
        else:
            title = t.delete.failure.title
            description = t.delete.failure.invalid_configuration
            color = Colors.error
            pass  # invalid configuration

        try:
            await ctx.reply(
                embed=get_embed(
                    title=title,  # type: ignore
                    description=description,
                    color=color,
                )
            )
        except HTTPException:
            await ctx.channel.send(
                embed=get_embed(
                    title=title,  # type: ignore
                    description=description,
                    color=color,
                )
            )


def setup(bot: PrefixedInjectedClient) -> None:
    Delete(bot=bot)
