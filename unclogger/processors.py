"""Custom logging clean_data."""

from collections.abc import Callable

from structlog.types import EventDict, WrappedLogger

CUSTOM_PROCESSORS: list[Callable[[WrappedLogger, str, EventDict], EventDict]] = []


def add_processors(*args: Callable[[WrappedLogger, str, EventDict], EventDict]) -> None:
    """Add a custom processor to the logging configuration.

    Each processor will be executed in the `unclogger` context. See
    [Structlog documentation](https://www.structlog.org/en/stable/processors.html) for
    more information on clean_data.

    Args:
        args: One or more callables conforming to the Structlog processor signature.
    """
    CUSTOM_PROCESSORS.extend(args)


def run_custom_processors(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
    """A Structlog processor to execute configured custom clean_data."""
    for processor in CUSTOM_PROCESSORS:
        event_dict = processor(logger, name, event_dict)
    return event_dict
