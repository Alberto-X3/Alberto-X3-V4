__all__ = ("NoAliasEnum",)


import sys
from aenum import NoAliasEnum as aNoAliasEnum
from typing import Any


class NoAliasEnum(aNoAliasEnum):
    @property
    def extension(self) -> str:
        if (package := sys.modules[self.__class__.__module__].__package__) is None:
            return ""
        return package.rsplit(".", 1)[-1]

    @property
    def fullname(self) -> str:
        return "{0.extension}:{0.name}".format(self)

    @property
    def default(self) -> Any:
        return self.value
