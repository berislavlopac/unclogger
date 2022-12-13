# Unclogger

`unclogger` is a simple library for customisable structured logging. It mirrors the standard Python logging library API, with a few additional functionalities.

!!! Info

    Implementation detail: `unclogger` is using the [Structlog library](https://www.structlog.org) under the hood.

## Structured Loggers

Passing keyword arguments to a log method will add them to the log data. Log data is converted to a JSON message before sending.

**Note:** The JSON in examples below was formatted for convenience; in practice it is sent as a single line of text.

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

The logger can be configured using the special attribute `config`. This can be used for configuring additional functionality, e.g. when [handling sensitive data](sensitive.md).

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

As can be seen in the error message above, `config` is an instance of [SimpleNamespace](https://docs.python.org/3.10/library/types.html#types.SimpleNamespace).


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

The [`context_bind`](reference.md#uncloggerloggercontext_bind) function will set values in the global context, where they can be used by any logger.

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
