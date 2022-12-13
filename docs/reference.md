# API Reference

## Logger

### ![mkapi](unclogger.get_logger)

### ![mkapi](unclogger.context_bind)

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

### ![mkapi](unclogger.set_level)

## Processors

### Sensitive Data

#### ![mkapi](unclogger.processors.clean_data.clean_sensitive_data)
