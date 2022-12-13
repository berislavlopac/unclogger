import logging

import pytest

from unclogger import set_level


def test_sets_default_log_level():
    # configure() is called at import time
    assert logging.root.level == logging.INFO


def test_sets_log_level_with_textual_parameter(caplog):
    with caplog.at_level(logging.INFO):
        assert logging.root.level == logging.INFO
        set_level("DEBUG")
        assert logging.root.level == logging.DEBUG
        set_level("error")
        assert logging.root.level == logging.ERROR


def test_sets_log_level_with_integer_parameter(caplog):
    with caplog.at_level(logging.INFO):
        assert logging.root.level == logging.INFO
        set_level(logging.DEBUG)
        assert logging.root.level == logging.DEBUG
        set_level(40)
        assert logging.root.level == logging.ERROR
        set_level("30")
        assert logging.root.level == logging.WARNING


@pytest.mark.parametrize("value", ("foo", "bar baz", 12.5, "12.5"))
def test_raises_an_exception_on_incorrect_argument(value):
    with pytest.raises(ValueError):
        set_level(value)
