__all__ = ("BanPermission",)


from aenum import auto
from typing import cast
from AlbertoX3.permission import BasePermission
from AlbertoX3.translations import t


class BanPermission(BasePermission):
    @property
    def description(self) -> str:
        return t.ban.permissions[self.name]

    ban = cast(BasePermission, auto())
    unban = cast(BasePermission, auto())
