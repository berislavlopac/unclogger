"""Custom logger with structured logging capabilities."""

import logging as _std_logging
import os
from typing import Any, cast, Optional, Union

import structlog

from .defaults import json_default
from .processors import clean_sensitive_data


# aliasing the type
class Unclogger(structlog.stdlib.BoundLogger):
    """Custom logger class."""

    @property
    def sensitive_keys(self) -> set:
        """Returns the custom set of sensitive keys set on the logger."""
        if not hasattr(self._logger, "sensitive_keys"):
            setattr(self._logger, "sensitive_keys", set())
        return getattr(self._logger, "sensitive_keys")

    @sensitive_keys.setter
    def sensitive_keys(self, value: set):
        """Sets the custom set of sensitive keys on the logger."""
        setattr(self._logger, "sensitive_keys", value)


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,  # type: ignore
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        clean_sensitive_data,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(default=json_default),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=Unclogger,
    cache_logger_on_first_use=True,
)


def configure(level: Union[int, str] = "", varname: str = "CLOGGER_LEVEL") -> None:
    """
    Set the basic configuration for new loggers.

    The level can be set by an environment variable, or passed as the level
    [name or number](https://docs.python.org/3/library/logging.html#logging-levels).

    Args:
        level: The level name or number.
        varname: Name of the environment variable to check for the level value.
                 The variable is only checked if the `level` is an empty string.
                 If neither is set, the default level is `logging.INFO`.

    Raises:
        ValueError if the level is not one of standard `logging` levels.
    """
    if level == "":
        level = os.getenv(varname, _std_logging.INFO)
    if isinstance(level, str):
        level = int(level) if level.isdigit() else _std_logging.getLevelName(level.upper())
    if not isinstance(level, int):
        raise ValueError(f"Incorrect log level '{level}'")
    _std_logging.basicConfig(format="%(message)s")
    _std_logging.getLogger().setLevel(level=level)


def get_logger(name: Optional[str] = None) -> Unclogger:
    """
    Retrieve a logger instance.

        >>> from unclogger import get_logger
        >>> unclogger = get_logger("unclogger")
        >>> unclogger.info("message")
        {"event": "message", "logger": "logger", "level": "info", "timestamp": "..."}

    The returned logger supports the standard Python logging protocol.

    Args:
        name: Optional name for the logger.
    """
    return cast(Unclogger, structlog.stdlib.get_logger(name).bind())


def context_bind(**kwargs: Any) -> None:
    """Inserts data into the global logging context.

    Args:
        kwargs: Any keyword argument will be inserted into the global context.
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def context_clear(*args: str) -> None:
    """Remove variables from context.

    Args:
        args: Keys for context variables to clear. If absent, all
              context variables are cleared.
    """
    if args:
        structlog.contextvars.unbind_contextvars(*args)
    else:
        structlog.contextvars.clear_contextvars()
