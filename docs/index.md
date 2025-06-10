# Introduction

**Unclogger** is a simple library for customisable structured logging. It mirrors the standard Python logging library API, with a few additional functionalities.

!!! Info "Implementation detail"

    Unclogger is using the [Structlog library](https://www.structlog.org) under the hood.

??? Note

    The JSON messages in examples below were formatted for convenience; in practice they are sent as a single line of text.

## Structured Loggers

Unclogger creates a logger object which adds one important functionality on top of the [standard logging library](https://docs.python.org/3/library/logging.html): in addition to a textual log message, any additional values passed to logging methods as keyword arguments will be included to the log context, along with a few standard fields:

* `event`: The original textual log message.
* `logger`: Name of the logger instance that created the message.
* `level`: The [log level](https://docs.python.org/3/library/logging.html#logging-levels) of the message.
* `timestamp`: Time date of the message in ISO 8601 format.

The final logging context will be converted and emitted as a JSON-formatted message.


!!! Example

    ```python
    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.info("test test", foo="abc", bar=123)
    {
        "foo": "abc", 
        "bar": 123, 
        "event": "test test", 
        "logger": "test logger", 
        "level": "info", 
        "timestamp": "2021-02-12T22:40:07.600385Z"
    }
    >>>
    ```

### Configuration

The logger can be configured using the special attribute `config`. This can be used for configuring additional functionality.

!!! Example

    ```python
    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.config.foo = "foo"
    >>> logger.config.bar = "bar"
    >>> print(logger.config.foo)
    foo
    >>> print(logger.config.bar)
    foo
    >>> print(logger.config.baz)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'types.SimpleNamespace' object has no attribute 'baz'. Did you mean: 'bar'?
    >>>
    ```

As can be seen in the error message above, `config` is an instance of [SimpleNamespace](https://docs.python.org/3/library/types.html#types.SimpleNamespace).


### Local Context

Each logger has a local context; values can be bound to it so they can appear in any message sent by that logger.

!!! Example

    ```python
    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger").bind(abc="def")
    >>> logger.info("test test", foo="abc", bar=123)
    {
        "abc": "def", 
        "foo": "abc", 
        "bar": 123, 
        "event": "test test", 
        "logger": "test logger", 
        "level": "info", "timestamp": 
        "2021-02-12T23:04:11.743922Z"
    }
    >>> # let's bind some more
    >>> import uuid
    >>> logger = logger.bind(some_uuid=uuid.uuid4())
    {
        "abc": "def", 
        "some_uuid": "88227c28-f5a6-430a-bdee-9e967c6c8d13",
        "foo": "abc", 
        "bar": 123, 
        "event": "test test", 
        "logger": "test logger", 
        "level": "info", 
        "timestamp": "2021-02-12T23:06:15.917766Z"
    }
    >>> # let's change a bound value
    >>> logger = logger.bind(abc="I have a new value now")
    >>> logger.info("test test", foo="abc", bar=123)
    {
        "abc": "I have a new value now",
        "some_uuid": "88227c28-f5a6-430a-bdee-9e967c6c8d13",
        "foo": "abc",
        "bar": 123,
        "event": "test test",
        "logger": "test logger",
        "level": "info",
        "timestamp": "2021-02-12T23:08:21.768578Z"
    }
    >>>
    ```


## Global Context

The [`context_bind`](reference.md#unclogger.context_bind) function will set values in the global context, where they can be used by any logger.

!!! Example

    ```python
    >>> from unclogger import get_logger, context_bind
    >>> # binding data before even creating a logger
    >>> context_bind(abc="def")
    >>> logger1 = get_logger("test logger 1")
    >>> logger1.info("test test", foo="abc", bar=123)
    {
        "abc": "def", 
        "foo": "abc", 
        "bar": 123, 
        "event": "test test", 
        "logger": "test logger 1", 
        "level": "info", 
        "timestamp": "2021-02-12T22:43:48.062282Z"
    }
    >>> logger2 = get_logger("test logger 2")
    >>> # a different logger can access the same data
    >>> logger2.info("another message")
    {
        "abc": "def", 
        "event": "another message", 
        "logger": "test logger 2", 
        "level": "info", "timestamp": 
        "2021-02-12T22:45:05.599852Z"
    }
    >>>
    ```

## Custom Processors

It is possible to add other `structlog` processors into the logger configuration. For example, to hide sensitive information that might be present in the logged data (using the [Sanitary](https://sanitary.readthedocs.io) library as an example):

!!! Example

    ```python
    >>> from sanitary import StructlogSanitizer
    >>> from unclogger import add_processors, get_logger
    >>>
    >>> add_processors(StructlogSanitizer(keys={"password", "email"}))
    >>>
    >>> logger = get_logger("test logger")
    >>> logger.info("test test", foo="abc", email="test@example.com", password="myPa55w0rd")
    {
        "foo": "abc", 
        "email": "********",
        "password": "********",
        "event": "test test", 
        "logger": "test logger", 
        "level": "info", 
        "timestamp": "2021-02-12T22:40:07.600385Z"
    }
    >>>
    ```

