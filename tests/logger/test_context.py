import json

import pytest

from unclogger import context_bind, context_clear, get_logger

LOG_METHODS = ("critical", "fatal", "debug", "error", "info", "warning")


@pytest.fixture(autouse=True)
def cleanup_context():
    yield
    context_clear()


@pytest.mark.parametrize("log_method", LOG_METHODS)
def test_globally_bound_data_is_included_in_log_output(caplog, log_method):
    log_level = ("critical" if log_method == "fatal" else log_method).upper()
    caplog.set_level(log_level.upper())
    message = "test message"
    logger_name = "test unclogger"

    context_bind(foo=123, bar="abc")

    logger = get_logger(logger_name)
    log_method = getattr(logger, log_method)  # extracted for parametrization
    log_method(message)

    record = json.loads(caplog.messages[0])
    assert len(record) == 6
    assert record["event"] == message
    assert record["level"] == log_level.lower()
    assert record["logger"] == logger_name
    assert "timestamp" in record
    assert record["foo"] == 123
    assert record["bar"] == "abc"


@pytest.mark.parametrize("log_method", LOG_METHODS)
def test_context_clear_without_arguments_removes_all_values(caplog, log_method):
    log_level = ("critical" if log_method == "fatal" else log_method).upper()
    caplog.set_level(log_level.upper())
    message = "test message"
    logger_name = "test unclogger"

    context_bind(foo=123, bar="abc")

    logger = get_logger(logger_name)
    log_method = getattr(logger, log_method)  # extracted for parametrization

    log_method(message)
    record_1 = json.loads(caplog.messages[0])
    assert record_1["foo"] == 123
    assert record_1["bar"] == "abc"

    context_clear()

    log_method(message)
    record_2 = json.loads(caplog.messages[1])
    assert "foo" not in record_2
    assert "bar" not in record_2


@pytest.mark.parametrize("log_method", LOG_METHODS)
def test_context_clear_with_arguments_removes_only_selected_values(caplog, log_method):
    log_level = ("critical" if log_method == "fatal" else log_method).upper()
    caplog.set_level(log_level.upper())
    message = "test message"
    logger_name = "test unclogger"

    context_bind(foo=123, bar="abc")

    logger = get_logger(logger_name)
    log_method = getattr(logger, log_method)  # extracted for parametrization

    log_method(message)
    record_1 = json.loads(caplog.messages[0])
    assert record_1["foo"] == 123
    assert record_1["bar"] == "abc"

    context_clear("foo")

    log_method(message)
    record_2 = json.loads(caplog.messages[1])
    assert "foo" not in record_2
    assert record_1["bar"] == "abc"
