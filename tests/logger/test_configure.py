import logging

import pytest

from unclogger import configure


def test_configure_sets_default_log_level():
    # configure() is called at import time
    assert logging.root.level == logging.INFO


def test_configure_sets_log_level_with_default_environment_variable(monkeypatch, caplog):
    monkeypatch.setenv("CLOGGER_LEVEL", "debug")
    with caplog.at_level(logging.INFO):
        assert logging.root.level == logging.INFO
        configure()
        assert logging.root.level == logging.DEBUG


def test_configure_sets_log_level_with_custom_environment_variable(monkeypatch, caplog):
    monkeypatch.setenv("FOO_BAR", "debug")
    with caplog.at_level(logging.INFO):
        assert logging.root.level == logging.INFO
        configure(varname="FOO_BAR")
        assert logging.root.level == logging.DEBUG


def test_configure_sets_log_level_with_textual_parameter(caplog):
    with caplog.at_level(logging.INFO):
        assert logging.root.level == logging.INFO
        configure("DEBUG")
        assert logging.root.level == logging.DEBUG
        configure("error")
        assert logging.root.level == logging.ERROR


def test_configure_sets_log_level_with_integer_parameter(caplog):
    with caplog.at_level(logging.INFO):
        assert logging.root.level == logging.INFO
        configure(logging.DEBUG)
        assert logging.root.level == logging.DEBUG
        configure(40)
        assert logging.root.level == logging.ERROR
        configure("30")
        assert logging.root.level == logging.WARNING


@pytest.mark.parametrize("value", ("foo", "bar baz", 12.5, "12.5"))
def test_configure_raises_an_exception_on_incorrect_argument(value):
    with pytest.raises(ValueError):
        configure(value)
