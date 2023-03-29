__all__ = (
    "get_utcnow",
    "get_value_table",
    "get_permissions",
    "get_language",
)


from datetime import datetime, timezone
from interactions.client.const import Absent
from interactions.models.discord.guild import Guild
from interactions.models.discord.snowflake import Snowflake_Type
from interactions.models.discord.user import Member, User
from pprint import pformat
from typing import Optional
from ..constants import MISSING, StyleConfig
from ..errors import DeveloperArgumentError
from ..permission import BasePermission


def get_utcnow() -> datetime:
    now = datetime.utcnow()
    utc = now.replace(tzinfo=timezone.utc)
    return utc


def get_value_table(obj: object, /, *, style: Absent[dict[str, str] | StyleConfig] = MISSING) -> str:
    """
    Creates a nice table with attributes and their values.

    Parameters
    ----------
    obj: object
        The object to get the values from.
    style: dict[str, str], StyleConfig
        The style to use. Defaults to StyleConfig.

    Returns
    -------
    str
        The value-table as a str.

    Examples
    --------
    >>> from AlbertoX3.utils import get_value_table
    >>> class Foo:
    ...     FOO = True
    ...     def __init__(self):
    ...         self.bar = "chocolate?"
    ...         self.spam = "EGG!!1!"
    >>> print(get_value_table(Foo))  # without __init__
    ... # ╔═══════════╤═══════╗
    ... # ║ Attribute │ Value ║
    ... # ╠═══════════╪═══════╣
    ... # ║ FOO       │ True  ║
    ... # ╚═══════════╧═══════╝
    >>> print(get_value_table(Foo()))  # with __init__
    ... # ╔═══════════╤══════════════╗
    ... # ║ Attribute │ Value        ║
    ... # ╠═══════════╪══════════════╣
    ... # ║ FOO       │ True         ║
    ... # ║ bar       │ 'chocolate?' ║
    ... # ║ spam      │ 'EGG!!1!'    ║
    ... # ╚═══════════╧══════════════╝
    """
    if style is MISSING:
        style = StyleConfig()
    if isinstance(style, dict):
        style = StyleConfig.from_dict(style)

    arguments: list[str] = [a for a in dir(obj) if not a.startswith("_")]
    values: list[str] = [pformat(getattr(obj, a), indent=0, depth=1, compact=True) for a in arguments]

    len_a: int = len(max(arguments + [style.t_attribute], key=len))
    len_v: int = len(max(values + [style.t_value], key=len))

    lines: list[str] = [
        f"{style.tl}{(len_a + 2) * style.ht}{style.tm}{(len_v + 2) * style.ht}{style.tr}",
        f"{style.vl} {style.t_attribute.ljust(len_a)} {style.vm} {style.t_value.ljust(len_v)} {style.vr}",
        f"{style.ml}{(len_a + 2) * style.hm}{style.mm}{(len_v + 2) * style.hm}{style.mr}",
    ]

    for a, v in zip(arguments, values):
        lines.append(
            f"{style.vl} {a.ljust(len_a)} {style.vm} {v.ljust(len_v)} {style.vr}",
        )

    lines.append(
        f"{style.bl}{(len_a + 2) * style.hb}{style.bm}{(len_v + 2) * style.hb}{style.br}",
    )

    return "\n".join(lines)


def get_permissions() -> list[BasePermission]:
    permissions: list[BasePermission] = []
    for bp_cls in BasePermission.__subclasses__():
        permissions.extend(list(bp_cls))
    return permissions


async def get_language(
    *, guild: Absent[Guild | Snowflake_Type] = MISSING, user: Absent[User | Member | Snowflake_Type] = MISSING
) -> Optional[str]:
    """
    Gets a set language by a guild or a user.

    **This function isn't completely implemented and returns ``None``.**
    **Besides that it already validates the given arguments.**

    Notes
    -----
    Only *one* argument can be set. Either ``guild`` *or* ``user``!

    Parameters
    ----------
    guild: Guild, SnowflakeType
        The guild to get the set language.
    user: User, Member, SnowflakeType
        The user to get the set language.

    Returns
    -------
    str, optional
        Returns the set language if one is set, otherwise None.

    Raises
    ------
    DeveloperArgumentError
        If either both (``guild`` and ``user``) or none of them are set.
    """
    # both are set
    if guild is not MISSING and user is not MISSING:
        raise DeveloperArgumentError("Can't set both ('guild' and 'user')!")
    # neither are set
    if guild is MISSING and user is MISSING:
        raise DeveloperArgumentError("Either 'guild' or 'user' have to be set!")

    # ToDo: connect to database
    return None
