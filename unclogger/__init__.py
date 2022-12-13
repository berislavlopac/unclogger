"""Simple library for customisable structured logging."""

import logging as _std_logging

from .logger import context_bind, context_clear, get_logger, set_level, Unclogger

getLogger = get_logger  # alias for compatibility with standard logging

_std_logging.basicConfig(format="%(message)s")
set_level()
