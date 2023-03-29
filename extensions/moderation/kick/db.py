__all__ = ("KickModel",)


from AlbertoX3.database import Base, UTCDatetime, db
from datetime import datetime
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer, Text


class KickModel(Base):
    __tablename__ = "kick"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    member: Column | int = Column(BigInteger, nullable=False)
    executor: Column | int = Column(BigInteger, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    reason: Column | str = Column(Text(128), nullable=False)

    @staticmethod
    async def add(member: int, executor: int, reason: str) -> "KickModel":
        return await db.add(
            KickModel(
                member=member,
                executor=executor,
                timestamp=datetime.utcnow(),
                reason=reason,
            )
        )
