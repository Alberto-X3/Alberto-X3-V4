__all__ = ("DurationConverter",)


from datetime import datetime, timedelta
from datetimeparser.datetimeparser import parse
from datetimeparser.utils.models import Result
from interactions.client.errors import BadArgument
from interactions.models.internal.context import BaseContext


class DurationConverter(timedelta):
    @staticmethod
    def convert(_: BaseContext, argument: str) -> timedelta:
        result: Result = parse(argument, "UTC")

        if result is None:
            raise BadArgument

        delta = result.time - datetime.utcnow()

        if delta <= timedelta(seconds=1):  # delta is around 0 or negative -> can't be good
            raise BadArgument

        return delta
