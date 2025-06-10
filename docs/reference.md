# API Reference

## Logger

::: unclogger.get_logger

::: unclogger.context_bind

## Global Log Level Configuration

??? Example

    ```python
    >>> from unclogger import get_logger, set_level
    >>> logger = get_logger("test logger")
    >>> logger.info("bar")
    {
        "event": "bar",
        "logger": "test logger",
        "level": "info",
        "timestamp": "2021-02-18T21:59:40.102272Z"
    }
    >>> logger.debug("bar")
    >>> set_level("debug")
    >>> logger.debug("bar")
    {
        "event": "bar",
        "logger": "test logger",
        "level": "debug",
        "timestamp": "2021-02-18T22:00:09.147106Z"
    }
    >>> set_level("warning")
    >>> logger.info("bar")
    >>>
    ```

::: unclogger.set_level

## Custom Processors

::: unclogger.processors.add_processors
