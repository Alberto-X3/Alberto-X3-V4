__all__ = (
    "get_extensions",
    "load_extensions",
    "check_extension_requirements",
    "get_subclasses_in_extensions",
)


import re
import sys
from interactions.client.client import Client
from interactions.client.const import Absent
from pathlib import Path
from typing import Iterable, cast, Literal, TypeVar
from ..constants import Config, MISSING
from ..errors import NoExtensionError, TooMayExtensionsError
from ..ipy_wrapper import Extension
from ..misc import EXTENSION_FEATURES, PrimitiveExtension
from .essentials import get_logger
from .terminal import get_installed_libraries


logger = get_logger()
T = TypeVar("T")
C = TypeVar("C", bound=type[object])


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
    # WARNING: don't read this code! It's a mess, and it works (somehow).
    #          Touching this function might end up destroying the whole startup of the bot!
    #          You've been warned!
    #          ~AlbertUnruh
    # ToDo: check; from ..ipy_wrapper import Extension

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
            logger.warning(f"Something unexpected happened during loading {extension.package!r}", exc_info=True)
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
                            lib, mode, ver = cast(re.Match[str], _LIB_REGEX.match(req)).groups()  # type: ignore
                            if (l_ver := libraries.get(lib, MISSING)) is MISSING:
                                disabled.add(extension)
                            if ver is not None and match_version(ver, f"{mode}=", l_ver):  # type: ignore
                                disabled.add(extension)
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


def match_version(v1: str, mode: Literal["==", "!=", ">=", "<=", "~="], v2: str) -> bool:
    """
    Matches ``v1`` against ``v2`` using ``mode``.

    Parameters
    ----------
    v1 str:
        Version A
    mode Literal["==", "!=", ">=", "<=", "~="]:
        The mode to check
    v2 str:
        Version B

    Returns
    -------
    bool
    """
    v1t: tuple[int, ...] = tuple(map(int, v1.split(".")))
    v2t: tuple[int, ...] = tuple(map(int, v2.split(".")))

    def unify_length(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
        m = max(len(o) for o in [a, b])
        a += (0,) * (m - len(a))
        b += (0,) * (m - len(b))
        return a, b

    v1t, v2t = unify_length(v1t, v2t)

    match mode:
        case "==":
            return v1t == v2t
        case "!=":
            return v1t != v2t
        case ">=":
            return v1t >= v2t
        case "<=":
            return v1t <= v2t
        case "~=":
            v1t, v2t = v1t + (0, 0), v2t + (0, 0)  # to ensure a length of at least 2
            return v1t[0] == v2t[0] and v1t[1:] >= v2t[1:]


def get_subclasses_in_extensions(base: C, *, extensions: Absent[Iterable[PrimitiveExtension]] = MISSING) -> list[C]:
    if extensions is MISSING:
        extensions = Config.EXTENSIONS

    packages: set[str] = {ext.package for ext in extensions}

    return [cls for cls in base.__subclasses__() if sys.modules[cls.__module__].__package__ in packages]
