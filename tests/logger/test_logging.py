import json
import logging
from types import SimpleNamespace

import pytest

from unclogger import get_logger, getLogger

LOG_METHODS = ("critical", "fatal", "debug", "error", "info", "warning")


def test_get_logger_returns_logger_instance():
    logger_name = "test logger"
    logger = get_logger(logger_name)

    # Note: we can't check using `isinstance` as `get_logger` returns a proxy
    # that instantiates our logger dynamically; but we can look for the attributes.
    assert logger.name == logger_name
    assert isinstance(logger.config, SimpleNamespace)


def test_getlogger_alias_returns_logger_instance():
    logger_name = "test logger"
    logger = getLogger(logger_name)

    # Note: we can't check using `isinstance` as `get_logger` returns a proxy
    # that instantiates our logger dynamically; but we can look for the attributes.
    assert logger.name == logger_name
    assert isinstance(logger.config, SimpleNamespace)


@pytest.mark.parametrize("log_method", LOG_METHODS)
def test_message_is_included_in_log_output_by_level_method(caplog, log_method):
    log_level = ("critical" if log_method == "fatal" else log_method).upper()
    caplog.set_level(log_level.upper())
    message = "test message"
    logger_name = "test logger"

    logger = get_logger(logger_name)
    log_method = getattr(logger, log_method)  # extracted for parametrization
    log_method(message)

    record = json.loads(caplog.messages[0])
    assert len(record) == 4
    assert record["event"] == message
    assert record["level"] == log_level.lower()
    assert record["logger"] == logger_name
    assert "timestamp" in record


@pytest.mark.parametrize("log_method", LOG_METHODS)
def test_message_is_included_in_log_output_by_log_method_with_numeric_level(caplog, log_method):
    log_level = ("critical" if log_method == "fatal" else log_method).upper()
    caplog.set_level(log_level.upper())
    message = "test message"
    logger_name = "test logger"
    log_level_int = logging.getLevelName(log_level)

    logger = get_logger(logger_name)
    logger.log(log_level_int, message)

    record = json.loads(caplog.messages[0])
    assert len(record) == 4
    assert record["event"] == message
    assert record["level"] == log_level.lower()
    assert record["logger"] == logger_name
    assert "timestamp" in record


@pytest.mark.parametrize("log_method", LOG_METHODS)
def test_message_with_formatting_is_included_in_log_output(caplog, log_method):
    log_level = ("critical" if log_method == "fatal" else log_method).upper()
    caplog.set_level(log_level.upper())
    message = "test message %s"
    logger_name = "test logger"

    logger = get_logger(logger_name)
    log_method = getattr(logger, log_method)  # extracted for parametrization
    log_method(message, 123)

    record = json.loads(caplog.messages[0])
    assert len(record) == 4
    assert record["event"] == "test message 123"
    assert record["level"] == log_level.lower()
    assert record["logger"] == logger_name
    assert "timestamp" in record


@pytest.mark.parametrize("log_method", LOG_METHODS)
def test_keyword_arguments_are_included_in_log_output(caplog, log_method):
    log_level = ("critical" if log_method == "fatal" else log_method).upper()
    caplog.set_level(log_level.upper())
    message = "test message"
    logger_name = "test logger"

    logger = get_logger(logger_name)
    log_method = getattr(logger, log_method)  # extracted for parametrization
    log_method(message, foo=123, bar="abc")

    record = json.loads(caplog.messages[0])
    assert len(record) == 6
    assert record["event"] == message
    assert record["level"] == log_level.lower()
    assert record["logger"] == logger_name
    assert "timestamp" in record
    assert record["foo"] == 123
    assert record["bar"] == "abc"


def test_exception_traceback_is_included_in_log_output_on_level_ERROR(caplog):
    caplog.set_level("ERROR")
    message = "test message"
    logger_name = "test logger"

    logger = get_logger(logger_name)

    try:
        raise RuntimeError("this is an error")  # noqa: TRY301, TRY003
    except RuntimeError:
        logger.exception(message, foo=123, bar="abc")

    record = json.loads(caplog.messages[0])
    assert len(record) == 7
    assert record["event"] == message
    assert record["level"] == "error"
    assert record["logger"] == logger_name
    assert "timestamp" in record
    assert record["exception"].startswith("Traceback")
    assert "RuntimeError: this is an error" in record["exception"]
