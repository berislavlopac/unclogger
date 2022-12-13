# Handling Sensitive Data

`unclogger` will automatically mask sensitive information such as PII, login credentials and the like. By default, the masked data is replaced by a generic string, which can be configured to use a hashing function instead.


## Sensitive Fields

If the name of any field in the structured log message matches one of the listed sensitive names, the value of that field is (recursively) replaced with a safe value:

    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.info("clean password", password="blabla", foo={"Email": "test@example.xcom"})
    {
        "password": "********",
        "foo": {"Email": "********"},
        "event": "clean password",
        "logger": "test logger",
        "level": "info",
        "timestamp": "2022-02-02T10:53:52.245833Z"
    }

A basic list of sensitive field names is included in `unclogger`:

    >>> from unclogger.processors.clean_data import SENSITIVE_FIELDS
    >>> SENSITIVE_FIELDS
    ['password', 'email', 'email_1', 'firstname', 'lastname', 'currentpassword', 'newpassword', 'tmppassword', 'authentication', 'refresh', 'auth', 'http_refresh', 'http_x_forwarded_authorization', 'http_x_endpoint_api_userinfo', 'http_authorization', 'idtoken', 'oauthidtoken', 'publickey', 'privatekey']

!!! Note

    Note that the list is case-insensitive; `unclogger` normalizes all field names to lowercase, so e.g. `email` and `Email` are treated equally.

This list can be configured with an iterable of custom field names:

    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.config.sensitive_keys = {"foo", "bar"}
    >>> logger.config.sensitive_keys.add("foobar")
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

### Configurable Replacement Value

A custom string can be used instead of the default replacement value:

    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.config.replacement = "blablabla"
    >>> logger.info("clean password", password="blabla", foo={"Email": "test@example.xcom"})
    {
        "password": "blablabla",
        "foo": {"Email": "blablabla"},
        "event": "clean password",
        "logger": "test logger",
        "level": "info",
        "timestamp": "2022-12-13T20:02:38.520599Z"
    }

### Hashing Sensitive Data

Instead of a replacement string, `config.replacement` can define a Python callable:

    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.config.replacement = hashlib.sha256
    >>> logger.info("clean password", password="blabla", foo={"Email": "test@example.xcom"})
    {
        "password": "ccadd99b16cd3d200c22d6db45d8b6630ef3d936767127347ec8a76ab992c2ea",
        "foo": {"Email": "77b6427267ac7638fd0cd49f2f64fd619ade2ab21d4a3891234293671c1d14b3"},
        "event": "clean password",
        "logger": "test logger",
        "level": "info",
        "timestamp": "2022-12-13T20:06:37.542212Z"
    }

This can be used so that the data can still be identified (e.g. an email address will always have the same has value) without sending the actual data to the log.

!!! Warning

    This functionality is intended to work out of the box with the functions present in the `hashlib` standard library. Any custom hash function has to accept a bytestring value and return a hash object as described in the [documentation](https://docs.python.org/3.10/library/hashlib.html). For typing purposes, `unclogger` provides a `Protocol` class for hash objects:
    
    ```python
    from unclogger.processors.clean_data import HashObjectProtocol
    
    def custom_hash_function(data: bytes) -> HashObjectProtocol:
        ...
    ```

## Sensitive Text Values
    >>> from unclogger import get_logger
    >>> logger = get_logger("test logger")
    >>> logger.info("'Authentication': 1234")
    {
        "event": "#### WARNING: Log message replaced due to sensitive keyword: 'Authentication':",
        "logger": "test logger",
        "level": "info",
        "timestamp": "2022-02-02T11:22:21.997204Z"
    }

*[PII]: Personally Identifiable Information