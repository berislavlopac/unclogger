import pytest
import structlog


@pytest.fixture(autouse=True)
def configure_structlog():
    """
    Change structlog configuration to enable testing.

    * Disable unclogger caching.
    """
    structlog.configure(cache_logger_on_first_use=False)
