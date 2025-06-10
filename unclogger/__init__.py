"""Simple library for customisable structured logging."""

import logging as _std_logging

from unclogger.logger import Unclogger, context_bind, context_clear, get_logger, set_level
from unclogger.processors import add_processors

getLogger = get_logger  # alias for compatibility with standard logging  # noqa: N816

_std_logging.basicConfig(format="%(message)s")
set_level()
