"""Custom logger with structured logging capabilities."""

import logging as _std_logging
from types import SimpleNamespace
from typing import Any, cast

import structlog

import unclogger.processors
from unclogger.defaults import json_default


# aliasing the type
class Unclogger(structlog.stdlib.BoundLogger):
    """Custom logger class."""

    @property
    def config(self) -> SimpleNamespace:
        """Simple configuration object for custom logger functionality."""
        if not hasattr(self._logger, "config"):
            self._logger.config = SimpleNamespace()  # type: ignore[attr-defined]
        return self._logger.config  # type: ignore[attr-defined]


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        unclogger.processors.run_custom_processors,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(default=json_default),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=Unclogger,
    cache_logger_on_first_use=True,
)


def set_level(level: int | str = _std_logging.INFO) -> None:
    """
    Sets the global logging level.

    The level can be passed as the level
    [name or number](https://docs.python.org/3/library/logging.html#logging-levels).

    Args:
        level: The level name or number.

    Raises:
        ValueError if the level is not one of standard `logging` levels.
    """
    if isinstance(level, str):
        level = int(level) if level.isdigit() else _std_logging.getLevelName(level.upper())
    if not isinstance(level, int):
        raise ValueError(f"Incorrect log level '{level}'")  # noqa: TRY003, TRY004
    _std_logging.getLogger().setLevel(level=level)


def get_logger(name: str | None = None) -> Unclogger:
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
    """
    Inserts data into the global logging context.

    Args:
        kwargs: Any keyword argument will be inserted into the global context.
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def context_clear(*args: str) -> None:
    """
    Remove variables from context.

    Args:
        args: Keys for context variables to clear. If absent, all
              context variables are cleared.
    """
    if args:
        structlog.contextvars.unbind_contextvars(*args)
    else:
        structlog.contextvars.clear_contextvars()
