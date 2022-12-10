"""Default functions for data serialisation."""

from datetime import date, datetime
from functools import singledispatch
from typing import Any
from uuid import UUID

from structlog.processors import _json_fallback_handler


@singledispatch
def json_default(value: Any) -> Any:
    """
    Default formatter for value types not supported by the `json` library.

    Currently supported types:

    * [UUID](https://docs.python.org/3/library/uuid.html#uuid.UUID)
    * [date](https://docs.python.org/3/library/datetime.html#date-objects)
    * [datetime](https://docs.python.org/3/library/datetime.html#datetime-objects)

    Any unsupported values will be converted to text using the `repr` function.
    """
    return _json_fallback_handler(value)


@json_default.register
def _uuid(value: UUID) -> str:
    return str(value)


@json_default.register
def _date(value: date) -> str:
    return value.isoformat()


@json_default.register
def _datetime(value: datetime) -> str:
    return value.isoformat() + "Z"
