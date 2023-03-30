__all__ = (
    "get_logger",
    "get_bool",
)


from vendor.AlbertUnruhUtils.utils.logger import (
    get_logger as auu_get_logger,
    _LOG_LEVEL_STR,  # noqa (_LOG_LEVEL_STR is not in __all__)
)
from logging import Logger
from typing import Optional, Union
from ..errors import UnrecognisedBooleanError


def get_logger(name: Optional[str] = None, level: Optional[_LOG_LEVEL_STR | int] = None) -> Logger:
    """
    Gets a logger.

    Parameters
    ----------
    name: str, optional
        The loggers name.
        If set to ``None`` name will be determined by ``__package__`` and ``__name__`` from globals.
    level: _LOG_LEVEL_STR, int, optional
        The loglevel for the logger.

    Returns
    -------
    Logger
        The created logger.
    """
    if name is None:
        import inspect

        frame = getattr(inspect.currentframe(), "f_back", None)
        if frame is not None:
            if (pkg := frame.f_globals["__package__"]).startswith(__package__.split(".", maxsplit=1)[0]):
                name = frame.f_globals["__name__"].split(".", maxsplit=1)[-1]
            else:
                # remove extension folder
                name = pkg.split(".", maxsplit=1)[-1]

    return auu_get_logger(name=name, level=level, add_handler=False)


def get_bool(obj: Union[bool, int, str, object], /) -> bool:
    """
    Currently matches:
        - True -> boolean, 1, lowered("true", "t", "yes", "y"), "1"
        - False -> boolean, -1, 0, lowered("false", "f", "no", "n"), "-1", "0"

    Parameters
    ----------
    obj: bool, int, str, object
        The object to match (should be bool, int or str; others aren't supported at the moment)

    Returns
    -------
    bool
        The matched boolean.

    Raises
    ------
    UnrecognisedBooleanError
        Raised when the object couldn't be matched to a boolean.
    """
    match obj:
        case bool():
            return obj  # type: ignore
        case int():
            match obj:
                case 1:
                    return True
                case -1 | 0:
                    return False
        case str():
            match obj.lower():  # type: ignore
                case "true" | "t" | "yes" | "y" | "1":
                    return True
                case "false" | "f" | "no" | "n" | "-1" | "0":
                    return False
    raise UnrecognisedBooleanError(obj)
