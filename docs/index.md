# Unclogger

`unclogger` is a simple library for customisable structured logging. It mirrors the standard Python logging library API, with a few additional functionalities.

## Examples

### Structured Logging

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

   
### Cleaning of Sensitive Values

`unclogger` provides support for hiding either sensitive fields (hiding the value of a key value pair if the key matches), or based on sensitive keywords within a string (hiding the whole string if the keyword is detected)

* Sensitive fields to be cleaned either come from the hardcoded list in `unclogger/processors` or can be provided to the logger object itself.
* Sensitive values are provided from the hardcode list in `unclogger/processors`


#### Hardcoded sensitive fields

If value is in the list of harcoded keywords then no further action is neccesary for the value to be hidden

    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.info("clean password", password="blabla")
    {'password': '********', 'event': 'clean password', 'logger': 'test logger', 'level': 'info', 'timestamp': '2022-02-02T10:53:52.245833Z'}

#### Provided sensitive fields

Keywords can be either added or set on the logger

    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.sensitive_keys = {"foo", "bar"}
    >>> logger.sensitive_keys.add("foobar")
    >>> payload = {"foo": "1234", "bar": "5678", "fooBar": "9876"}
    >>> logger.info("clean sensitive values)", payload=payload)
    {'payload': {'foo': '********', 'bar': '********', 'fooBar': '********'}, 'event': 'clean sensitive values', 'logger': 'test logger', 'level': 'info', 'timestamp': '2022-02-02T11:08:01.260019Z'}    logger.sensitive_keys = {"foo", "bar"}

#### Sensitive values
    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.info("'Authentication': 1234")
    {'event': "The content of this message has been replaced because the following keyword was detected: 'Authentication':", 'logger': 'test logger', 'level': 'info', 'timestamp': '2022-02-02T11:22:21.997204Z'}