__all__ = (
    "MuteModel",
    "UnmuteModel",
)


from AlbertoX3.database import Base, UTCDatetime, db
from datetime import datetime
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer, Text


class MuteModel(Base):
    __tablename__ = "mute"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    member: Column | int = Column(BigInteger, nullable=False)
    executor: Column | int = Column(BigInteger, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    reason: Column | str = Column(Text(128), nullable=False)
    until: Column | datetime = Column(UTCDatetime, nullable=True)

    @staticmethod
    async def add(member: int, executor: int, reason: str, until: datetime | None) -> "MuteModel":
        return await db.add(
            MuteModel(
                member=member,
                executor=executor,
                timestamp=datetime.utcnow(),
                reason=reason,
                until=until,
            )
        )


class UnmuteModel(Base):
    __tablename__ = "unmute"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    member: Column | int = Column(BigInteger, nullable=False)
    executor: Column | int = Column(BigInteger, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    reason: Column | str = Column(Text(128), nullable=False)

    @staticmethod
    async def add(member: int, executor: int, reason: str) -> "UnmuteModel":
        return await db.add(
            UnmuteModel(
                member=member,
                executor=executor,
                timestamp=datetime.utcnow(),
                reason=reason,
            )
        )
