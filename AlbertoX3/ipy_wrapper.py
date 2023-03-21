__all__ = ("Extension",)


from interactions.models.internal.command import BaseCommand as ipy_BaseCommand
from interactions.models.internal.extension import Extension as ipy_Extension
from interactions.models.internal.listener import Listener as ipy_Listener
from interactions.models.internal.tasks.task import Task as ipy_Task
from typing import TypeVar, ParamSpec, Callable, Awaitable, TypedDict, Required, Any
from .database import db_wrapper
from .translations import language_wrapper
from .utils import get_logger


logger = get_logger(__name__)
T = TypeVar("T")
P = ParamSpec("P")


def multi_wrap(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    if getattr(func, "_is_multi_wrapped_by_ipy_wrapper", False) is False:
        func = db_wrapper(language_wrapper(func))
        func._is_multi_wrapped_by_ipy_wrapper = True
    return func


class _Requirements(TypedDict):
    """Means ``dict[Literal["lib", "ext"], list[str]]`` and translates to ``{"lib": [], "ext": []}``"""

    lib: Required[list[str]]
    ext: Required[list[str]]


class Extension(ipy_Extension):
    enabled: bool
    """Whether this extension is enabled or not. If enabled it may be disabled if requirements aren't met."""
    requires: _Requirements
    """Any required libraries or extensions (used to determine whether the extension *can* be enabled or not)."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls._sanity_check()
        for attr in dir(cls):
            val = getattr(cls, attr)
            if isinstance(val, ipy_BaseCommand):
                if val.checks:
                    val.checks = [multi_wrap(check) for check in val.checks]
                if val.error_callback:
                    val.error_callback = multi_wrap(val.error_callback)
                if val.pre_run_callback:
                    val.pre_run_callback = multi_wrap(val.pre_run_callback)
                if val.post_run_callback:
                    val.post_run_callback = multi_wrap(val.post_run_callback)
            if isinstance(val, (ipy_BaseCommand, ipy_Listener, ipy_Task)):
                if val.callback:
                    val.callback = multi_wrap(val.callback)

    @classmethod
    def _sanity_check(cls) -> bool:
        all_good = True

        if not hasattr(cls, "enabled"):
            all_good = False
            cls.enabled = False
            logger.warning(
                f"Attribute 'enabled' not set in Extension {cls.__name__}! Automatically set it to False (disabled)..."
            )

        if not hasattr(cls, "requires"):
            all_good = False
            cls.requires = {"lib": [], "ext": []}
            logger.warning(
                f"Attribute 'requires' not set in Extension {cls.__name__}! Assuming no dependencies at all..."
            )

        if cls.requires.get("lib") is None:
            all_good = False
            cls.requires["lib"] = []
            logger.warning(
                f"Attribute 'requires' in Extension {cls.__name__} has no libraries set! Assuming no dependencies..."
            )

        if cls.requires.get("ext") is None:
            all_good = False
            cls.requires["ext"] = []
            logger.warning(
                f"Attribute 'requires' in Extension {cls.__name__} has no extensions set! Assuming no dependencies..."
            )

        return all_good
