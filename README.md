Unclogger
=========

Simple Python library for customizable structured logging.

[![Documentation Status](https://readthedocs.org/projects/unclogger/badge/?version=latest)](https://unclogger.readthedocs.io/en/latest/?badge=latest)

## Quick Intro

 ```python
from unclogger import get_logger
logger = get_logger("test logger")
logger.info("test test", foo="abc", bar=123)
```

Output:
```json
{
  "foo": "abc", 
  "bar": 123, 
  "event": "test test", 
  "logger": "test logger", 
  "level": "info", 
  "timestamp": "2021-02-12T22:40:07.600385Z"
}
```
