"""Custom processor for cleaning sensitive data."""
# pylint: disable=unused-argument
from __future__ import annotations

import json
import os
from collections import ChainMap
from decimal import Decimal
from functools import singledispatch
from typing import Any, Callable, Iterable, Optional, Protocol, Union

from structlog.types import EventDict, WrappedLogger


class HashObjectProtocol(Protocol):
    """
    Protocol for objects returned by the `hashlib` library functions.

    See `hashlib` documentation for details:
    https://docs.python.org/3.10/library/hashlib.html
    """

    @property
    def block_size(self) -> int:
        """The internal block size of the hash algorithm in bytes."""

    @property
    def digest_size(self) -> int:
        """The size of the resulting hash in bytes."""

    @property
    def name(self) -> str:
        """
        The canonical name of this hash.

        Always lowercase and always suitable as a parameter to new()
        to create another hash of this type.
        """

    def copy(self) -> HashObjectProtocol:
        """
        Returns an identical copy of the hash object.

        This can be used to efficiently compute the digests of data
        sharing a common initial substring.
        """

    def digest(self, length: Optional[int] = None) -> str:
        """
        Return the digest of the data passed to the update() method so far.

        This is a bytes object of size digest_size which may contain bytes in the
        whole range from 0 to 255.

        The SHAKE algorithms provide variable length digests with
        `length_in_bits//2` up to 128 or 256 bits of security, so their digest
        methods require a length.

        Args:
            length: Optional length in bytes, required of SHAKE algorithms.
        """

    def hexdigest(self, length: Optional[int] = None) -> str:
        """
        Like `digest()`, except containing only hexadecimal digits.

        This may be used to exchange the value safely in email or other
        non-binary environments.

        Args:
            length: Optional length in bytes, required of SHAKE algorithms.
        """

    def update(self, obj: bytes, /) -> None:
        """
        Update the hash object with the bytes-like object.

        Repeated calls are equivalent to a single call with the concatenation of
        all the arguments: m.update(a); m.update(b) is equivalent to m.update(a+b).

        Args:
            obj: The byte-string to concatenate to the previous value.
        """


ReplacementType = Union[str, Callable[[bytes], HashObjectProtocol]]

SENSITIVE_FIELDS = [
    "password",
    "email",
    "email_1",
    "firstname",
    "lastname",
    "currentpassword",
    "newpassword",
    "tmppassword",
    "authentication",
    "refresh",
    "auth",
    "http_refresh",
    "http_x_forwarded_authorization",
    "http_x_endpoint_api_userinfo",
    "http_authorization",
    "idtoken",
    "oauthidtoken",
    "publickey",
    "privatekey",
]
SENSITIVE_KEYWORDS = [
    """'Authentication':""",
    """"Authentication":""",
    """'Refresh':""",
    """"Refresh":""",
    """'Bearer """,
    """"Bearer """,
    "Bearer ",
]

DEFAULT_REPLACEMENT: str = os.getenv("UNCLOGGER_REPLACEMENT", default="********")
REPLACEMENT_MESSAGE = "#### WARNING: Log message replaced due to sensitive keyword: "


def clean_sensitive_data(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
    """
    Clean up logging context to mask potentially sensitive information.

    This function follows the standard
    [Structlog processor API](https://www.structlog.org/en/stable/processors.html).

    Args:
        logger: The logger instance doing the logging.
        name: Name of the logging method, e.g. `info` or `warning`.
        event_dict: Current context, including modifications by other processors.

    Returns:
        dict
    """
    return _clean_up(event_dict, logger)


@singledispatch
def _clean_up(data, logger):
    return _clean_up(str(data), logger)


@_clean_up.register(float)
@_clean_up.register(int)
def _clean_up_number(data, logger):
    return data


@_clean_up.register
def _clean_up_decimal(data: Decimal, logger):
    return float(data)


@_clean_up.register
def _clean_up_str(data: str, logger):
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        data_lower = data.lower()
        for sensitive_keyword in SENSITIVE_KEYWORDS:
            if sensitive_keyword.lower() in data_lower:
                return REPLACEMENT_MESSAGE + sensitive_keyword
        return data
    else:
        return _clean_up(data, logger)


@_clean_up.register(set)
@_clean_up.register(tuple)
@_clean_up.register(list)
def _clean_up_sequence(data, logger):
    return [_clean_up(value, logger) for value in data]


@_clean_up.register
def _clean_up_dict(data: dict, logger):
    sensitive_keys: Iterable[str] = ()
    if hasattr(logger, "config") and hasattr(logger.config, "sensitive_keys"):
        sensitive_keys = logger.config.sensitive_keys
    sensitive_fields = {field.lower() for field in [*SENSITIVE_FIELDS, *sensitive_keys]}
    cleaned_data = ChainMap({}, data)
    replacement: ReplacementType = DEFAULT_REPLACEMENT
    if hasattr(logger, "config") and hasattr(logger.config, "replacement"):
        replacement = logger.config.replacement
    for key, value in cleaned_data.items():
        cleaned_data[key] = (
            _replace(value, replacement)
            if key.lower() in sensitive_fields
            else _clean_up(value, logger)
        )
    return dict(cleaned_data)


def _replace(value: Any, replacement: ReplacementType):
    if callable(replacement):
        replaced = replacement(str(value).encode())
        if "shake_" in replacement.__name__:
            return replaced.hexdigest(256)
        return replaced.hexdigest()
    return replacement
