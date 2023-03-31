__all__ = ("Ban",)


from datetime import datetime, timedelta
from typing import cast

from interactions.client.errors import NotFound, Forbidden
from interactions.ext.prefixed_commands.command import prefixed_command
from interactions.ext.prefixed_commands.context import PrefixedContext
from interactions.ext.prefixed_commands.manager import PrefixedInjectedClient
from interactions.models.discord.user import User, Member
from interactions.models.internal.checks import guild_only
from interactions.models.internal.command import check
from interactions.models.internal.listener import listen
from interactions.models.internal.tasks.task import Task
from interactions.models.internal.tasks.triggers import IntervalTrigger, DateTrigger

from AlbertoX3.converters import DurationConverter
from AlbertoX3.database import db, filter_by
from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.translations import TranslationNamespace, t  # type: ignore
from AlbertoX3.utils.essentials import get_logger
from AlbertoX3.utils.general import get_utcnow
from AlbertoX3.utils.ipy import get_embed

from .colors import Colors
from .db import BanModel, UnbanModel
from .permission import BanPermission
from .settings import BanSettings


logger = get_logger()
tg: TranslationNamespace = cast(TranslationNamespace, t.g)
t: TranslationNamespace = cast(TranslationNamespace, t.ban)


class Ban(Extension):
    enabled = True
    requires = {"lib": [], "ext": []}

    @listen()
    async def on_startup(self):
        self.unban_task.start()
        await self.reschedule_unban_task()

    async def reschedule_unban_task(self) -> None:
        date = cast(datetime, (await BanModel.get_next_to_check()).until)
        # need to do some magic (get the timedelta) to make the date from aware to naive
        self.unban_task.reschedule(DateTrigger(datetime.now() + (date - get_utcnow())))
        if self.unban_task.next_run is None:
            # one unban-check may be missed (either the bot was offline or the ban-interval was just absurdly short*)
            #                                *which idiot bans someone for a few seconds?!
            idiot_notice = "" if self.unban_task.iteration == 0 else " Which idiot bans that short?!?!?!"
            logger.warning("Rescheduling unban-task now!" + idiot_notice)  # yes, it has to be
            self.unban_task._fire(datetime.now())  # noqa
        else:
            logger.info(f"Rescheduled unban-task: {self.unban_task.next_run}")

    # the IntervalTrigger is just the trigger during startup, then it's date-based
    # it will never be triggered since during startup the task is immediately rescheduled
    @Task.create(IntervalTrigger(minutes=1))
    async def unban_task(self) -> None:
        logger.debug("Starting unban-task")
        try:
            ban: BanModel
            async for ban in await db.stream(filter_by(BanModel, until_checked=False)):
                if (user := await self.bot.fetch_user(ban.member)) is not None:
                    user = user.tag
                else:
                    ban.until_checked = True
                    logger.info(f"User {ban.member} no longer exists! Can't unban them...")
                    continue

                if ban.until is None:
                    ban.until_checked = True
                    continue
                if ban.until > get_utcnow():
                    continue

                try:
                    await self.bot.guilds[0].unban(user=ban.member, reason=ban.reason + " | @unban due to limited ban")
                except NotFound:
                    ban.until_checked = True
                    logger.info(f"Unable to unban user {user} ({ban.member})! They aren't banned on the server!")
                except Forbidden:
                    logger.info(
                        f"Unable to unban user {user} ({ban.member})! I don't have enough permissions on the server!"
                    )
                else:
                    await UnbanModel.add(
                        ban.member, self.bot.user.id, ban.reason + " | @unban due to limited ban"  # type: ignore
                    )
                    ban.until_checked = True
                    logger.info(f"Automatically unbanned user {user} ({ban.member}); initial reason: {ban.reason}")
        finally:
            await self.reschedule_unban_task()

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
                await ctx.guild.ban(
                    user=user,
                    reason=reason,
                    delete_message_seconds=await BanSettings.delete_message_seconds.get(),
                )
            except Forbidden:
                title = t.ban.failure.title
                description = t.ban.failure.missing_permissions(user=user.mention)
                color = Colors.missing_permissions
            else:
                await BanModel.add(user.id, ctx.author.id, reason, until)
                await self.reschedule_unban_task()
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
            await self.reschedule_unban_task()
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
