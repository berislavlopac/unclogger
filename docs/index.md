# Unclogger

`unclogger` is a simple library for customisable structured logging. It mirrors the standard Python logging library API, with a few additional functionalities.

## Structured Logging

Passing keyword arguments to a log method will add them to the log data. Log data is converted to a JSON message before sending.

**Note:** The JSON in examples below was formatted for convenience; in practice it is sent as a single line of text.

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


### Configuration

The logger can be configured using the special attribute `config`:

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

As can be seen in the error message above, `config` is an instance of [SimpleNamespace](https://docs.python.org/3.10/library/types.html#types.SimpleNamespace).


### Global Context Binding

The [`context_bind`](reference.md#uncloggerloggercontext_bind) function will set values in the global context, where it can be used by any logger.

    >>> from unclogger import get_logger, bind_data
    >>> # binding data before even creating a logger
    >>> bind_data(abc="def")
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

### Local Context Binding

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

### Logging Level Configuration

    >>> from unclogger import get_logger, configure
    >>> logger = get_logger("test logger")
    >>> logger.info("bar")
    {"event": "bar", "logger": "test logger", "level": "info", "timestamp": "2021-02-18T21:59:40.102272Z"}
    >>> logger.debug("bar")
    >>> configure("debug")
    >>> logger.debug("bar")
    {"event": "bar", "logger": "test logger", "level": "debug", "timestamp": "2021-02-18T22:00:09.147106Z"}
    >>> configure("warning")
    >>> logger.info("bar")
