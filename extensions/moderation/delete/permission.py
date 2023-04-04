__all__ = ("DeletePermission",)


from aenum import auto
from typing import cast
from AlbertoX3.permission import BasePermission
from AlbertoX3.translations import t


class DeletePermission(BasePermission):
    @property
    def description(self) -> str:
        return t.delete.permissions[self.name]

    delete = cast(BasePermission, auto())
