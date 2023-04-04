__all__ = (
    "DurationConverter",
    "IntConverter",
)


from datetime import datetime, timedelta
from datetimeparser.datetimeparser import parse
from datetimeparser.utils.models import Result
from interactions.client.errors import BadArgument
from interactions.models.internal.context import BaseContext
from typing import Self
from .errors import DeveloperArgumentError


class DurationConverter(timedelta):
    @staticmethod
    def convert(_: BaseContext, argument: str) -> timedelta:
        result: Result = parse(argument, "UTC")

        if result is None:
            raise BadArgument

        delta = result.time - datetime.utcnow()

        return delta


class IntConverter(int):
    min: int = None  # noqa: A003
    max: int = None  # noqa: A003

    @classmethod
    def with_range(cls, min: int, max: int) -> Self:  # noqa: A003
        if min > max:
            raise DeveloperArgumentError(f"min is higher than max! {min} > {max}")
        converter = cls()
        converter.min = min
        converter.max = max
        return converter

    def convert(self, _: BaseContext, argument: str) -> int:
        try:
            val = int(argument)
        except ValueError as e:
            raise BadArgument from e

        if self.min is not None:
            if val < self.min:
                raise BadArgument(f"argument smaller than {self.min}!")
        if self.max is not None:
            if val > self.max:
                raise BadArgument(f"argument bigger than {self.max}!")

        return val
