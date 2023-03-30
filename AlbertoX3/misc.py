# NOTE: this file may be subject to change completely!

__all__ = (
    "FormatStr",
    "EXTENSION_FEATURES",
    "PrimitiveExtension",
)


from abc import ABC, abstractmethod
from interactions.client.const import MISSING
from pathlib import Path
from typing import Callable, Iterable, Literal, Any
from .utils.essentials import get_logger


logger = get_logger()


class FormatStr(str):
    __call__: Callable[..., str] = str.format
    __getattribute__: Callable[[str, str], Any] = str.__getattribute__  # to confuse pyright ^^


_EXTENSION_FEATURES = Literal["ext", "colors", "db", "permissions", "settings", "stats"]

# only public because this might be of interest and not in .constants since it's required in here
EXTENSION_FEATURES: tuple[_EXTENSION_FEATURES] = _EXTENSION_FEATURES.__args__  # type: ignore


class ExtensionFeaturesGenerator(ABC):
    """
    Automatically generates a property for every feature.
    """

    @abstractmethod
    def _has(self, i: int) -> bool:
        ...

    def __init_subclass__(cls) -> None:
        if cls.__base__ != ExtensionFeaturesGenerator:
            # already subclassed
            return

        for i, feature in enumerate(EXTENSION_FEATURES):
            name = f"has_{feature.lower()}"
            exec(  # noqa S102
                "def {0}(self): return self._has({1})".format(name, i),
                env := globals().copy(),
            )
            setattr(cls, name, property(env[name]))
            logger.info(f"Added method {name} to {cls.__name__}")


class PrimitiveExtension(ExtensionFeaturesGenerator):
    folder: str
    """The folder in which the groups are"""
    group: str
    """The group in which the extension is present"""
    name: str
    """The name of the extension"""
    path: Path
    """The path to the extension"""
    features: int
    """The features encoded in an integer (check attribute ``has_FEATURE_NAME`` (lower case))"""

    def __init__(self, folder: str, group: str, name: str, path: Path, *, has: Iterable[_EXTENSION_FEATURES] = MISSING):
        self.folder = folder
        self.group = group
        self.name = name
        self.path = path

        self.features = 0
        if has is not MISSING:
            for i, feature in enumerate(EXTENSION_FEATURES):
                if feature not in has:
                    continue
                self.features += 1 << i

    @property
    def full_name(self) -> str:
        return "{0.group}.{0.name}".format(self)

    @property
    def package(self) -> str:
        return "{0.folder}.{0.full_name}".format(self)

    def _has(self, i: int) -> bool:
        return (self.features & (1 << i)) == (1 << i)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name!r} ({self.features})>"
