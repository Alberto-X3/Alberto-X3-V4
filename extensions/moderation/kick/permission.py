__all__ = ("KickPermission",)


from aenum import auto
from AlbertoX3.permission import BasePermission
from AlbertoX3.translations import t


class KickPermission(BasePermission):
    @property
    def description(self) -> str:
        return t.kick.permissions[self.name]

    kick = auto()
