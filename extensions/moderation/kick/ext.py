__all__ = ("Kick",)


from typing import cast

from interactions.client.errors import Forbidden
from interactions.ext.prefixed_commands.command import prefixed_command
from interactions.ext.prefixed_commands.context import PrefixedContext
from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient
from interactions.models.discord.user import User, Member
from interactions.models.internal.checks import guild_only
from interactions.models.internal.command import check

from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.translations import TranslationNamespace, t  # type: ignore
from AlbertoX3.utils.essentials import get_logger
from AlbertoX3.utils.ipy import get_embed

from ...moderation.ban.settings import BanSettings
from .colors import Colors
from .db import KickModel
from .permission import KickPermission


logger = get_logger()
tg: TranslationNamespace = cast(TranslationNamespace, t.g)
t: TranslationNamespace = cast(TranslationNamespace, t.kick)


class Kick(Extension):
    enabled = True
    requires = {"lib": [], "ext": ["moderation.ban"]}

    @prefixed_command(name="kick", aliases=[])
    @check(guild_only())
    @KickPermission.kick.check
    async def ban(
        self,
        ctx: PrefixedContext,
        user: User,
        *,
        reason: str,
    ):
        author: Member = await ctx.bot.fetch_member(ctx.author_id, ctx.guild_id)  # type: ignore
        victim: Member | None = await ctx.bot.fetch_member(user.id, ctx.guild_id)
        if (victim is None) or (author.top_role > victim.top_role):
            # Two hierarchies are allowed for kicking:
            #   A: victim is not on the server
            #   B: author is higher than victim (higher role)
            try:
                await ctx.guild.kick(user=user, reason=reason)
            except Forbidden:
                title = t.kick.failure.title
                description = t.kick.failure.missing_permissions(user=user.mention)
                color = Colors.missing_permissions
            else:
                await KickModel.add(user.id, ctx.author.id, reason)
                title = t.kick.success.title
                description = t.kick.success.info(user=user.mention, reason=reason)
                color = Colors.kick
        else:
            title = t.kick.failure.title
            description = t.kick.failure.hierarchie(user=user.mention)
            color = Colors.missing_permissions

        await ctx.reply(
            embed=get_embed(
                title=title,  # type: ignore
                description=description,
                color=color,
            )
        )

    @prefixed_command(name="hardkick", aliases=[])
    @check(guild_only())
    @KickPermission.hardkick.check
    async def hardkick(
        self,
        ctx: PrefixedContext,
        user: User,
        *,
        reason: str,
    ):
        author: Member = await ctx.bot.fetch_member(ctx.author_id, ctx.guild_id)  # type: ignore
        victim: Member | None = await ctx.bot.fetch_member(user.id, ctx.guild_id)
        if (victim is None) or (author.top_role > victim.top_role):
            # Two hierarchies are allowed for hardkicking:
            #   A: victim is not on the server
            #   B: author is higher than victim (higher role)
            try:
                await ctx.guild.ban(
                    user=user,
                    reason=reason + " | @hardkick",
                    delete_message_seconds=await BanSettings.delete_message_seconds.get(),
                )
                await ctx.guild.unban(user=user, reason=reason + " | @hardkick")
            except Forbidden:
                title = t.hardkick.failure.title
                description = t.hardkick.failure.missing_permissions(user=user.mention)
                color = Colors.missing_permissions
            else:
                await KickModel.add(user.id, ctx.author.id, reason, True)
                title = t.hardkick.success.title
                description = t.hardkick.success.info(user=user.mention, reason=reason)
                color = Colors.hardkick
        else:
            title = t.hardkick.failure.title
            description = t.hardkick.failure.hierarchie(user=user.mention)
            color = Colors.missing_permissions

        await ctx.reply(
            embed=get_embed(
                title=title,  # type: ignore
                description=description,
                color=color,
            )
        )


def setup(bot: PrefixedInjectedClient) -> None:
    Kick(bot=bot)
