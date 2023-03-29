__all__ = ("BanPermission",)


from aenum import auto
from AlbertoX3.permission import BasePermission
from AlbertoX3.translations import t


class BanPermission(BasePermission):
    @property
    def description(self) -> str:
        return t.ban.permissions[self.name]

    ban = auto()
    unban = auto()
    tempban = auto()
