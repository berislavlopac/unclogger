"""Simple library for customisable structured logging.]"""

from .logger import configure, context_bind, context_clear, get_logger, Unclogger

getLogger = get_logger  # alias for compatibility with standard logging

configure()
