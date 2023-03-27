__all__ = (
    "get_logger",
    "get_utcnow",
    "get_value_table",
    "get_bool",
    "get_lib_version",
    "get_installed_libraries",
    "get_extensions",
    "load_extensions",
    "get_subclasses_in_extensions",
    "get_permissions",
    "get_language",
    "get_member",
    "get_user",
)


import re
import sys
from datetime import datetime, timezone
from interactions.client.client import Client
from interactions.client.const import Absent
from interactions.models.discord.guild import Guild
from interactions.models.discord.snowflake import Snowflake_Type
from interactions.models.discord.user import Member, User
from interactions.models.internal.context import BaseContext
from pathlib import Path
from pprint import pformat
from typing import Optional, TypeVar, Iterable, cast, Literal
from .constants import Config, LIB_PATH, MISSING, StyleConfig
from .errors import DeveloperArgumentError, NoExtensionError, TooMayExtensionsError
from .misc import EXTENSION_FEATURES, PrimitiveExtension
from .permission import BasePermission
from ._utils_essentials import get_bool, get_logger


logger = get_logger()
T = TypeVar("T")
C = TypeVar("C", bound=type[object])


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


_VERSION_REGEX: re.Pattern[str] = re.compile(r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", re.MULTILINE)


def get_lib_version() -> str:
    file = LIB_PATH.joinpath("__init__.py").read_text("utf-8")
    version: str
    if (result := _VERSION_REGEX.search(file)) is None:
        version = "0.0.0"
    else:
        version = result.group(1)

    try:
        import subprocess  # noqa S404

        out: bytes
        err: bytes

        # commit count
        p = subprocess.Popen(  # noqa S603, S607
            ["git", "rev-list", "--count", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += f"+{out.decode('utf-8').strip()}"

        # commit sha
        p = subprocess.Popen(  # noqa S603, S607
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += f"+g{out.decode('utf-8').strip()}"

    except Exception as e:  # noqa: F841  # ToDo: logging
        ...

    return version


def get_installed_libraries() -> dict[str, str]:
    """
    Gets every installed library via ``pip list``

    Returns
    -------
    dict[str, str]
        A dictionary with {package: version}.
    """
    import subprocess  # noqa: S404

    out: bytes
    err: bytes
    p: str
    v: str
    libraries: dict[str, str] = {}

    out, err = subprocess.Popen(  # noqa S603, S607
        ["pip", "list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()

    if out:
        for pkg in out.decode().splitlines(keepends=False):
            p, v = pkg.split()
            if p == "Package" and v == "Version":
                continue
            if max(map(lambda s: len(s.replace("-", "")), [p, v])) == 0:
                continue
            libraries[p] = v

    return libraries


def get_extensions(folder: Absent[Path] = MISSING) -> set[PrimitiveExtension]:
    if folder is MISSING:
        folder = Config.EXTENSIONS_FOLDER

    extensions: set[PrimitiveExtension] = set()

    for group in filter(Path.is_dir, folder.iterdir()):
        for ext in filter(Path.is_dir, group.iterdir()):
            py_files = [e.name.removesuffix(".py") for e in ext.iterdir() if e.is_file() and e.name.endswith(".py")]
            if "ext" not in py_files:
                # isn't a valid extension
                continue

            features = {f for f in py_files if f in EXTENSION_FEATURES}
            extensions.add(
                PrimitiveExtension(
                    folder=folder.name, group=group.name, name=ext.name, path=ext, has=features  # type: ignore
                )
            )

    return extensions


def load_extensions(bot: Client, extensions: Absent[Iterable[PrimitiveExtension]] = MISSING) -> None:
    if extensions is MISSING:
        extensions = get_extensions()

    # get enabled extensions
    enabled = check_extension_requirements(extensions)

    for extension in enabled:
        logger.info(f"Loading extension {extension.full_name!r}")
        bot.load_extension(name=f"{extension.package}.ext")

    skipped = {ext for ext in extensions if ext not in enabled}
    if skipped:
        logger.info(f"Skipped loading following extensions: {', '.join([ext.full_name for ext in skipped])}")


_LIB_REGEX: re.Pattern[str] = re.compile(r"^([a-zA-Z][\w-]*)(?:([=!><~])=(\d[\d.]*))?$")


def check_extension_requirements(extensions: Absent[Iterable[PrimitiveExtension]] = MISSING) -> set[PrimitiveExtension]:
    """
    Checks all requirements listed in ``Extension.requirements``

    Parameters
    ----------
    extensions: Absent[Iterable[PrimitiveExtension]]
        All extensions to check among each other.

    Returns
    -------
    set[PrimitiveExtension]
        All extensions with met requirements (and are enabled).
    """
    # ToDo: respect ``Extension.requires["lib"]`` version
    # WARNING: don't read this code! It's a mess, and it works (somehow).
    #          Touching this function might end up destroying the whole startup of the bot!
    #          You've been warned!
    #          ~AlbertUnruh
    from .ipy_wrapper import Extension

    if extensions is MISSING:
        extensions = get_extensions()

    ext_classes: set[tuple[PrimitiveExtension, type[Extension]]] = set()
    disabled: set[PrimitiveExtension] = set()
    required_by: dict[str, list[tuple[PrimitiveExtension, type[Extension]]]] = {}
    libraries: dict[str, str] = get_installed_libraries()
    lib: str
    mode: Literal["=", "!", ">", "<", "~"] | None
    ver: str | None
    l_ver: str

    # get all (by default) disabled extensions (and fill in ext_classes)
    for extension in extensions:
        try:
            __import__(f"{extension.package}.ext")
        except BaseException:  # noqa: F841  # something is wrong with the extension... missing imports? syntax errors?
            logger.warning(f"Something unexpected happened during loading {extension.package!r}")
            disabled.add(extension)
        else:
            ext_cls = get_subclasses_in_extensions(base=Extension, extensions=[extension])
            match len(ext_cls):
                case 0:  # no Extension
                    raise NoExtensionError(extension)
                case 1:  # perfect!
                    ext_classes.add((extension, cls := ext_cls[0]))
                    if not cls.enabled:
                        disabled.add(extension)
                    else:
                        for req in cls.requires["lib"]:
                            lib, mode, ver = cast(re.Match[str], _LIB_REGEX.match(req)).groups()
                            if (l_ver := libraries.get(lib, MISSING)) is MISSING:
                                disabled.add(extension)
                            if ver is not None:  # specific version is set
                                logger.warning(
                                    f"Version specification isn't supported at the moment! "
                                    f"`{lib} {mode}= {ver}` specified, `{l_ver}`is given; no checks ran"
                                )
                case _:  # more than one!
                    raise TooMayExtensionsError(extension)

    # get all dependencies
    for ext in ext_classes:
        for dep in ext[1].requires["ext"]:
            required_by.setdefault(dep, []).append(ext)

    ext_names = [ext[0].full_name for ext in ext_classes]
    dis_names = [ext.full_name for ext in disabled]
    unsatisfied: list[str] = [dep for dep in required_by if dep not in ext_names or dep in dis_names]

    while unsatisfied:
        dependency = unsatisfied.pop()
        if dependency not in required_by:
            continue
        for ext, _ in required_by[dependency]:
            if ext.full_name in dis_names:
                continue
            disabled.add(ext)
            dis_names.append(ext.full_name)
            unsatisfied.append(ext.full_name)

    return {ext[0] for ext in ext_classes} - disabled


def get_subclasses_in_extensions(base: C, *, extensions: Absent[Iterable[PrimitiveExtension]] = MISSING) -> list[C]:
    if extensions is MISSING:
        extensions = Config.EXTENSIONS

    packages: set[str] = {ext.package for ext in extensions}

    return [cls for cls in base.__subclasses__() if sys.modules[cls.__module__].__package__ in packages]


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
