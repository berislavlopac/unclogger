"""Custom logging clean_data."""

from collections.abc import Callable

from structlog.types import EventDict, WrappedLogger

# A dict (with `None` values) rather than a set: dicts preserve insertion order, so
# registered processors run in a deterministic order, while still deduping by identity.
CUSTOM_PROCESSORS: dict[Callable[[WrappedLogger, str, EventDict], EventDict], None] = {}


def add_processors(*args: Callable[[WrappedLogger, str, EventDict], EventDict]) -> None:
    """Add a custom processor to the logging configuration.

    Each processor will be executed in the `unclogger` context. See
    [Structlog documentation](https://www.structlog.org/en/stable/processors.html) for
    more information on clean_data.

    Args:
        args: One or more callables conforming to the Structlog processor signature.
    """
    for arg in args:
        CUSTOM_PROCESSORS[arg] = None


def run_custom_processors(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
    """A Structlog processor to execute configured custom clean_data."""
    for processor in CUSTOM_PROCESSORS:
        event_dict = processor(logger, name, event_dict)
    return event_dict
