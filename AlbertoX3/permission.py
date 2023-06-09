__all__ = (
    "permission_override",
    "PermissionModel",
    "BasePermission",
    "BasePermissionLevel",
    "PermissionLevel",
    "check_permission_level",
)


import sys
from aenum import Enum
from collections import namedtuple
from contextvars import ContextVar
from interactions.models.discord.user import Member, User
from interactions.models.internal.command import check
from interactions.models.internal.context import BaseContext
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String
from typing import Awaitable, Callable, cast
from .database import Base, db, redis
from .environment import CACHE_TTL
from .errors import UnrecognisedPermissionLevelError


permission_override: ContextVar["BasePermissionLevel"] = ContextVar("permission_override")


class PermissionModel(Base):
    __tablename__ = "permissions"

    permission: str | Column = Column(String(64), primary_key=True, unique=True, nullable=False)
    level: int | Column = Column(Integer, nullable=False)

    @staticmethod
    async def create(permission: str, level: int) -> "PermissionModel":
        return await db.add(PermissionModel(permission=permission, level=level))

    @staticmethod
    async def get(permission: str, default: int) -> int:
        if (value := await redis.execute_command("GET", rkey := f"permissions:{permission}")) is not None:
            return int(value)

        if (row := await db.get(PermissionModel, permission=permission)) is None:
            row = await PermissionModel.create(permission=permission, level=default)

        await redis.execute_command("SETEX", rkey, CACHE_TTL, cast(int, row.level))
        return cast(int, row.level)

    @staticmethod
    async def set(permission: str, level: int) -> "PermissionModel":  # noqa A003
        await redis.execute_command("SETEX", f"permissions:{permission}", CACHE_TTL, level)

        if (row := await db.get(PermissionModel, permission=permission)) is None:
            row = await PermissionModel.create(permission=permission, level=level)

        row.level = level
        return row


class BasePermission(Enum):
    @property
    def description(self) -> str:
        raise NotImplementedError

    @property
    def ext(self) -> str:
        return (sys.modules[self.__class__.__module__].__package__ or "").rsplit(".", maxsplit=1)[-1]

    @property
    def fullname(self) -> str:
        return "{0.ext}.{0.name}".format(self)

    @property
    def _default_level(self) -> "BasePermissionLevel":
        from .constants import Config

        defaults = cast(dict[str, dict[str, BasePermissionLevel]], Config.PERMISSION_DEFAULT_OVERRIDES)
        return defaults.get(self.ext, {}).get(self.name, Config.PERMISSION_DEFAULT_LEVEL)

    async def resolve(self) -> "BasePermissionLevel":
        from .constants import Config

        value: int = await PermissionModel.get(self.fullname, self._default_level.level)
        for level in Config.PERMISSION_LEVELS:  # type: ignore
            if level.level == value:
                return level
        raise UnrecognisedPermissionLevelError(level=value)

    async def set(self, level: "BasePermissionLevel") -> None:  # noqa A003
        await PermissionModel.set(self.fullname, level.level)

    async def check_permissions(self, user: Member | User) -> bool:
        return await (await self.resolve()).check_permissions(user)

    @property
    def check(self) -> Callable[[BaseContext], Awaitable[bool]]:
        return check_permission_level(self)


PermissionLevel = namedtuple("PermissionLevel", ["level", "aliases", "description", "guild_permissions", "roles"])


class BasePermissionLevel(Enum):
    @property
    def level(self) -> int:
        return self.value.level

    @property
    def aliases(self) -> list[str]:
        return self.value.aliases

    @property
    def description(self) -> str:
        return self.value.description

    @property
    def guild_permissions(self) -> list[str]:
        return self.value.guild_permissions

    @property
    def roles(self) -> list[str]:
        return self.value.roles

    @classmethod
    async def get_permission_level(cls, user: Member | User) -> "BasePermissionLevel":
        if override := permission_override.get(None):
            return override

        return await cls._get_permission_level(user)

    @classmethod
    async def _get_permission_level(cls, user: Member | User) -> "BasePermissionLevel":
        raise NotImplementedError

    async def check_permissions(self, user: Member | User) -> bool:
        level: BasePermissionLevel = await self.get_permission_level(user)
        return level.level >= self.level

    @property
    def check(self) -> Callable[[BaseContext], Awaitable[bool]]:
        return check_permission_level(self)

    @classmethod
    def max(cls) -> "BasePermissionLevel":  # noqa A003
        return max(cls, key=lambda x: x.level)


def check_permission_level(level: BasePermission | BasePermissionLevel) -> Callable[[BaseContext], Awaitable[bool]]:
    async def inner(ctx: BaseContext) -> bool:
        user = ctx.author
        if not await level.check_permissions(user):
            return False
        return True

    inner.level = level

    return check(inner)  # type: ignore
