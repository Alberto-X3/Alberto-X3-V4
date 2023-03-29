__all__ = ("DeleteModel",)


from AlbertoX3.database import Base, UTCDatetime, db
from datetime import datetime
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer


class DeleteModel(Base):
    __tablename__ = "delete"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    amount: Column | int = Column(Integer, nullable=False)
    channel: Column | int = Column(BigInteger, nullable=False)
    executor: Column | int = Column(BigInteger, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    user: Column | int = Column(BigInteger, nullable=True)

    @staticmethod
    async def add(amount: int, channel: int, executor: int, user: int | None) -> "DeleteModel":
        return await db.add(
            DeleteModel(
                amount=amount,
                channel=channel,
                executor=executor,
                timestamp=datetime.utcnow(),
                user=user,
            )
        )
