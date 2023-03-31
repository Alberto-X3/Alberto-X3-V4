__all__ = (
    "BanModel",
    "UnbanModel",
)

from AlbertoX3.database import Base, UTCDatetime, db, select
from datetime import datetime
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer, Text, Boolean


class BanModel(Base):
    __tablename__ = "ban"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    member: Column | int = Column(BigInteger, nullable=False)
    executor: Column | int = Column(BigInteger, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    reason: Column | str = Column(Text(128), nullable=False)
    until: Column | datetime = Column(UTCDatetime, nullable=True)
    until_checked: Column | bool = Column(Boolean, default=False, nullable=False)

    @staticmethod
    async def add(member: int, executor: int, reason: str, until: datetime | None) -> "BanModel":
        return await db.add(
            BanModel(
                member=member,
                executor=executor,
                timestamp=datetime.utcnow(),
                reason=reason,
                until=until,
            )
        )

    @staticmethod
    async def get_next_to_check() -> "BanModel":
        next_until = await db.first(
            # select(func.min(BanModel.until)).filter(BanModel.until >= get_utcnow()).filter_by(until_checked=False)
            # get the first unchecked one instead of the next one to unban
            select(func.min(BanModel.until)).filter_by(until_checked=False)
        )
        return await db.get(BanModel, until=next_until)  # type: ignore


class UnbanModel(Base):
    __tablename__ = "unban"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    member: Column | int = Column(BigInteger, nullable=False)
    executor: Column | int = Column(BigInteger, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    reason: Column | str = Column(Text(128), nullable=False)

    @staticmethod
    async def add(member: int, executor: int, reason: str) -> "UnbanModel":
        return await db.add(
            UnbanModel(
                member=member,
                executor=executor,
                timestamp=datetime.utcnow(),
                reason=reason,
            )
        )
