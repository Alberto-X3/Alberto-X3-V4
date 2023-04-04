__all__ = (
    "AlbertoX3Error",
    "DeveloperError",
    "InternalNotImplementedError",
    "DeveloperArgumentError",
    "UnrecognisedPermissionLevelError",
    "InvalidPermissionLevelError",
    "GatherAnyError",
    "UnrecognisedBooleanError",
    "TranslationError",
    "UnsupportedTranslationTypeError",
    "UnsupportedLanguageError",
    "DatabaseError",
    "NoActiveSessionError",
    "ExtensionError",
    "ExtensionLoadingError",
    "NoExtensionError",
    "TooMayExtensionsError",
)


from interactions.client.const import Absent, MISSING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .misc import PrimitiveExtension


class AlbertoX3Error(Exception):
    """
    Base for every Exception from AlbertoX3.
    """


class DeveloperError(AlbertoX3Error):
    pass


class InternalNotImplementedError(DeveloperError, NotImplementedError):
    func_o_meth_o_mod: str
    """--> Function or Method or Module"""

    def __init__(self, func_o_meth_o_mod: str):
        self.func_o_meth_o_mod = func_o_meth_o_mod

    def __str__(self) -> str:
        return f"{self.func_o_meth_o_mod} is not implemented!"


class DeveloperArgumentError(DeveloperError):
    pass


class UnrecognisedPermissionLevelError(DeveloperArgumentError, ValueError):
    level: int

    def __init__(self, level: int):
        self.level = level

    def __str__(self) -> str:
        return f"Permission level {self.level} not found!"


class InvalidPermissionLevelError(DeveloperArgumentError, ValueError):
    level: int

    def __init__(self, level: int):
        self.level = level

    def __str__(self) -> str:
        return f"Permission level has to be higher than 0 and not {self.level}!"


class GatherAnyError(AlbertoX3Error):
    idx: int
    exception: Exception

    def __init__(self, idx: int, exception: Exception):
        self.idx = idx
        self.exception = exception

    def __str__(self) -> str:
        # it may be changed in the future as I'll detect more edge-cases
        return f"An error occurred in coroutine {self.idx} while gathering: {self.exception}"


class UnrecognisedBooleanError(AlbertoX3Error):
    obj: object

    def __init__(self, obj: object):
        self.obj = obj

    def __str__(self) -> str:
        return f"Unable to assign {self.obj.__class__.__qualname__} with value {self.obj!r} to either True or False!"


class TranslationError(AlbertoX3Error):
    pass


class UnsupportedTranslationTypeError(TranslationError):
    key: str
    type: object  # noqa: A003
    supported: list[object]

    def __init__(self, key: str, type: object, supported: Absent[list[object]] = MISSING):  # noqa: A002
        self.key = key
        self.type = type
        if supported is MISSING:
            self.supported = []
        else:
            self.supported = supported

    def __str__(self) -> str:
        return f"Unsupported type {self.type!r} for {self.key!r}!" + (
            f" Following types are supported: {', '.join(f'{s!r}' for s in self.supported)}" if self.supported else ""
        )


class UnsupportedLanguageError(TranslationError):
    language: str
    supported: list[str]

    def __init__(self, language: str, supported: Absent[list[str]] = MISSING):
        self.language = language
        if supported is MISSING:
            from .constants import Config

            self.supported = Config.LANGUAGE_AVAILABLE
        else:
            self.supported = supported

    def __str__(self) -> str:
        return f"Unsupported language {self.language!r}! Supported languages are: {', '.join(self.supported)}"


class DatabaseError(AlbertoX3Error):
    pass


class NoActiveSessionError(DatabaseError):
    def __str__(self) -> str:
        return "There is no active database session in this context!"


class ExtensionError(AlbertoX3Error):
    pass


class ExtensionLoadingError(ExtensionError):
    extension: "PrimitiveExtension"

    def __init__(self, extension: "PrimitiveExtension"):
        self.extension = extension


class NoExtensionError(ExtensionLoadingError):
    def __str__(self) -> str:
        return f"No extension class could be found in {self.extension.package}!"


class TooMayExtensionsError(ExtensionLoadingError):
    def __str__(self) -> str:
        return f"Too many extensions classes found in {self.extension.package}!"
