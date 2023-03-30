__all__ = ("KickPermission",)


from aenum import auto
from typing import cast
from AlbertoX3.permission import BasePermission
from AlbertoX3.translations import t


class KickPermission(BasePermission):
    @property
    def description(self) -> str:
        return t.kick.permissions[self.name]

    kick = cast(BasePermission, auto())
    hardkick = cast(BasePermission, auto())
