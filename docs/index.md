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

   
## Cleaning Sensitive Data

`unclogger` provides support for hiding either sensitive fields (hiding the value of a key/value pair if the key matches), or based on sensitive keywords within a string (hiding the whole string if a keyword is detected).

* A base list of sensitive key names is hard-coded in `unclogger`; this list can be either expanded or replaced with custom names.
* Sensitive values are provided from the hardcode list in `unclogger/processors`

### Sensitive Field Names

If the name of any field in the structured log message matches one of the listed sensitive names, the value of that field is (recursively) replaced with a safe value:

    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.info("clean password", password="blabla", foo={"email": "test@example.xcom"})
    {
        "password": "********",
        "foo": {"email": "********"},
        "event": "clean password",
        "logger": "test logger",
        "level": "info",
        "timestamp": "2022-02-02T10:53:52.245833Z"
    }

A basic list of sensitive key names is hard-coded in `unclogger`; this list can be expanded with custom names:

    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.sensitive_keys = {"foo", "bar"}
    >>> logger.sensitive_keys.add("foobar")
    >>> payload = {"foo": "1234", "bar": "5678", "fooBar": "9876"}
    >>> logger.info("clean sensitive values)", payload=payload)
    {
        "payload": {
            "foo": "********",
            "bar": "********",
            "fooBar": "********"
        },
        "event": "clean sensitive values",
        "logger": "test logger",
        "level": "info",
        "timestamp":
        "2022-02-02T11:08:01.260019Z"
    }

### Sensitive Text Values
    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.info("'Authentication': 1234")
    {
        "event": "#### WARNING: Log message replaced due to sensitive keyword: 'Authentication':",
        "logger": "test logger",
        "level": "info",
        "timestamp": "2022-02-02T11:22:21.997204Z"
    }