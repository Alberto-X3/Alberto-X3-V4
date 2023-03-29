__all__ = (
    "BanModel",
    "UnbanModel",
)


from AlbertoX3.database import Base, UTCDatetime, db
from datetime import datetime
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer, Text


class BanModel(Base):
    __tablename__ = "ban"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    member: Column | int = Column(BigInteger, nullable=False)
    executor: Column | int = Column(BigInteger, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    reason: Column | str = Column(Text(128), nullable=False)
    until: Column | datetime = Column(UTCDatetime, nullable=True)

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
