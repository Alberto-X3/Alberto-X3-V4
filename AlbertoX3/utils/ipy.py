__all__ = (
    "get_embed",
    "get_member",
    "get_user",
)


import re
from interactions.models.discord.snowflake import Snowflake_Type
from interactions.models.discord.embed import Embed, EmbedField, EmbedAuthor, EmbedAttachment, EmbedFooter
from interactions.models.discord.timestamp import Timestamp
from interactions.models.discord.user import Member, User
from interactions.models.internal.context import BaseContext
from typing import Optional, cast
from ..colors import AllColors


def get_embed(
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[int] = AllColors.default,
    url: Optional[str] = None,
    timestamp: Optional[Timestamp | bool] = True,
    fields: Optional[list[EmbedField]] = None,
    author: Optional[EmbedAuthor] = None,
    thumbnail: Optional[EmbedAttachment] = None,
    images: Optional[list[EmbedAttachment]] = None,
    footer: Optional[EmbedFooter] = None,
) -> Embed:
    """Basically the same as ``interactions.Embed()``, but with default values."""
    if timestamp is False:
        timestamp = None
    elif timestamp is True:
        timestamp = Timestamp.utcnow()
    cast(Optional[Timestamp], timestamp)

    return Embed(
        title=title,
        description=description,
        color=color,
        url=url,
        timestamp=timestamp,
        fields=fields or [],
        author=author,
        thumbnail=thumbnail,
        images=images or [],
        footer=footer,
    )


_ID_REGEX: re.Pattern[str] = re.compile(r"^([1-9]\d{6,19})$")
_MENTION_REGEX: re.Pattern[str] = re.compile(r"^<@!?([1-9]\d{6,19})>$")
_NAME_REGEX: re.Pattern[str] = re.compile(r"^(.{2,32})#(\d{4})$")


async def get_member(ctx: BaseContext, raw: User | Member | Snowflake_Type) -> Optional[Member]:
    """
    Get a member from the context's guild.

    Parameters
    ----------
    ctx: BaseContext
    raw: Member, User, Snowflake_Type
        The member to find.

    Returns
    -------
    Member, optional
        The found member.
    """
    match raw:
        case Member():
            return raw

        case User():
            return await ctx.bot.fetch_member(ctx.guild_id, raw.id)

        case _ if _ID_REGEX.match(str(raw)) is not None:  # also covers int() via regex
            return await ctx.bot.fetch_member(ctx.guild_id, int(raw))

        case int():
            # only invalid id's get here
            return None

        case str():
            # mention?
            if (result := _MENTION_REGEX.match(raw)) is not None:
                return await ctx.bot.fetch_member(ctx.guild_id, result.group(1))

            # try name.lower if name doesn't match
            for converter in (str, str.lower):
                raw = converter(raw)

                # name#discriminator?
                if (result := _NAME_REGEX.match(raw)) is not None:
                    name, discriminator = result.groups()
                    for member in ctx.guild.members:
                        if converter(member.username) == name and member.discriminator == discriminator:
                            return member

                # name?
                for member in ctx.guild.members:
                    if converter(member.username) == raw:
                        return member

                # nick?
                for member in ctx.guild.members:
                    if converter(member.nickname) == raw:
                        return member

        case _ if hasattr(raw, "__int__"):
            # maybe a SnowflakeObject was passed
            return await get_member(ctx, int(raw))

        case _:
            return None


async def get_user(ctx: BaseContext, raw: User | Member | Snowflake_Type) -> Optional[User]:
    """
    Parameters
    ----------
    ctx: BaseContext
    raw: User, Member, Snowflake_Type
        The user to search for.

    Returns
    -------
    User, optional
        The found user.
    """
    match raw:
        case User():
            return raw

        case Member():
            return raw.user

        case _ if _ID_REGEX.match(str(raw)) is not None:  # also covers int() via regex
            return await ctx.bot.fetch_user(int(raw))

        case int():
            # only invalid id's get here
            return None

        case str():
            # mention?
            if (result := _MENTION_REGEX.match(raw)) is not None:
                return await ctx.bot.fetch_user(result.group(1))

            # try name.lower if name doesn't match
            for converter in (str, str.lower):
                raw = converter(raw)

                # name#discriminator?
                if (result := _NAME_REGEX.match(raw)) is not None:
                    name, discriminator = result.groups()
                    for user in ctx.bot.cache.user_cache.values():
                        if converter(user.username) == name and user.discriminator == discriminator:
                            return user

                # name?
                for user in ctx.bot.cache.user_cache.values():
                    if converter(user.username) == raw:
                        return user

        case _ if hasattr(raw, "__int__"):
            # maybe a SnowflakeObject was passed
            return await get_user(ctx, int(raw))

        case _:
            return None
