__all__ = ("Ban",)


from datetime import timedelta
from typing import cast

from interactions.client.errors import NotFound, Forbidden
from interactions.ext.prefixed_commands.command import prefixed_command
from interactions.ext.prefixed_commands.context import PrefixedContext
from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient
from interactions.models.discord.user import User, Member
from interactions.models.internal.checks import guild_only
from interactions.models.internal.command import check

from AlbertoX3.converters import DurationConverter
from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.translations import TranslationNamespace, t  # type: ignore
from AlbertoX3.utils.essentials import get_logger
from AlbertoX3.utils.general import get_utcnow
from AlbertoX3.utils.ipy import get_embed

from .colors import Colors
from .db import BanModel, UnbanModel
from .permission import BanPermission


logger = get_logger()
tg: TranslationNamespace = cast(TranslationNamespace, t.g)
t: TranslationNamespace = cast(TranslationNamespace, t.ban)


class Ban(Extension):
    enabled = True

    # ToDo: add task to automatically unban banned members

    @prefixed_command(name="ban", aliases=[])
    @check(guild_only())
    @BanPermission.ban.check
    async def ban(
        self,
        ctx: PrefixedContext,
        user: User,
        duration: DurationConverter = timedelta.max,  # type: ignore
        *,
        reason: str,
    ):
        if duration > timedelta(days=366 * 5):  # ~5 years
            until = None
        else:
            until = get_utcnow() + duration

        author: Member = await ctx.bot.fetch_member(ctx.author_id, ctx.guild_id)  # type: ignore
        victim: Member | None = await ctx.bot.fetch_member(user.id, ctx.guild_id)
        if (victim is None) or (author.top_role > victim.top_role):
            # Two hierarchies are allowed for banning:
            #   A: victim is not on the server
            #   B: author is higher than victim (higher role)
            try:
                await ctx.guild.ban(user=user, reason=reason)
            except Forbidden:
                title = t.ban.failure.title
                description = t.ban.failure.missing_permissions(user=user.mention)
                color = Colors.missing_permissions
            else:
                await BanModel.add(user.id, ctx.author.id, reason, until)
                if until is not None:
                    end = t.ban.success.until_date(timestamp=until.timestamp())
                else:
                    end = t.ban.success.until_eternity
                title = t.ban.success.title
                description = t.ban.success.info(user=user.mention, end=end, reason=reason)
                color = Colors.ban
        else:
            title = t.ban.failure.title
            description = t.ban.failure.hierarchie(user=user.mention)
            color = Colors.missing_permissions

        await ctx.reply(
            embed=get_embed(
                title=title,  # type: ignore
                description=description,
                color=color,
            )
        )

    @prefixed_command(name="unban", aliases=[])
    @check(guild_only())
    @BanPermission.unban.check
    async def unban(
        self,
        ctx: PrefixedContext,
        user: User,
        *,
        reason: str,
    ):
        try:
            await ctx.guild.unban(user=user, reason=reason)
        except NotFound:
            title = t.unban.failure.title
            description = t.unban.failure.not_banned(user=user.mention)
            color = Colors.not_found
        except Forbidden:
            title = t.unban.failure.title
            description = t.unban.failure.missing_permissions(user=user.mention)
            color = Colors.missing_permissions
        else:
            await UnbanModel.add(user.id, ctx.author.id, reason)
            title = t.unban.success.title
            description = t.unban.success.info(user=user.mention, reason=reason)
            color = Colors.unban

        await ctx.reply(
            embed=get_embed(
                title=title,  # type: ignore
                description=description,
                color=color,
            )
        )


def setup(bot: PrefixedInjectedClient) -> None:
    Ban(bot=bot)
