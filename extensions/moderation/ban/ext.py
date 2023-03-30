__all__ = ("Ban",)


from datetime import timedelta
from typing import cast

from interactions.ext.prefixed_commands.command import prefixed_command
from interactions.ext.prefixed_commands.context import PrefixedContext
from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient
from interactions.models.discord.embed import Embed
from interactions.models.discord.user import Member, User

from AlbertoX3.converters import DurationConverter
from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.translations import TranslationNamespace, t  # type: ignore
from AlbertoX3.utils.essentials import get_logger
from AlbertoX3.utils.general import get_utcnow

from .db import BanModel, UnbanModel
from .permission import BanPermission


logger = get_logger()
tg: TranslationNamespace = cast(TranslationNamespace, t.g)
t: TranslationNamespace = cast(TranslationNamespace, t.ban)


class Ban(Extension):
    enabled = True

    # ToDo: add task to automatically unban banned members

    @prefixed_command(name="ban", aliases=[])
    @BanPermission.ban.check
    async def ban(
        self,
        ctx: PrefixedContext,
        member: Member,
        duration: DurationConverter = timedelta.max,  # type: ignore
        *,
        reason: str,
    ):
        if duration > timedelta(days=366 * 5):  # 5 years
            until = None
        else:
            until = get_utcnow() + duration

        await member.ban(reason=reason)
        await BanModel.add(member.id, ctx.author.id, reason, until)

        # ToDo: make response prettier
        if until is not None:
            await ctx.reply(
                embed=Embed(description=f"Banned {member} until <t:{round(until.timestamp())}:F>: `{reason}`")
            )
        else:
            await ctx.reply(embed=Embed(description=f"Banned {member}: `{reason}`"))

    @prefixed_command(name="unban", aliases=[])
    @BanPermission.unban.check
    async def unban(
        self,
        ctx: PrefixedContext,
        user: User,
        *,
        reason: str,
    ):
        await ctx.guild.unban(user, reason)
        await UnbanModel.add(user.id, ctx.author.id, reason)

        # ToDo: make response prettier
        await ctx.reply(embed=Embed(description=f"unbanned {user}: `{reason}`"))


def setup(bot: PrefixedInjectedClient) -> None:
    Ban(bot=bot)
