"""Custom processor for cleaning sensitive data."""
# pylint: disable=unused-argument

import hashlib
import json
import os
from collections import ChainMap
from decimal import Decimal
from functools import singledispatch
from typing import Any

from structlog.types import EventDict, WrappedLogger

# TODO: enable setting field names ad keywords in external configuration files
SENSITIVE_FIELD_NAMES = [
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

REPLACEMENT_TEXT = os.getenv("UNCLOGGER_REPLACEMENT", default="********")
REPLACEMENT = getattr(hashlib, REPLACEMENT_TEXT, REPLACEMENT_TEXT)
REPLACEMENT_MESSAGE = "#### WARNING: Log message replaced due to sensitive keyword: "


def clean_sensitive_data(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
    """
    Clean up logging context to mask potentially sensitive personal information.

    For example: In case of any accidental logging of user authentication tokens/credentials,
    this processor would prevent them from being logged. It will replace the offending message
    with a standard one stating by which exactly blacklisted keyword/string was triggered.

    Args:
        logger:
        name:
        event_dict:

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
    sensitive_fields = {
        field.lower()
        for field in [*SENSITIVE_FIELD_NAMES, *getattr(logger, "sensitive_keys", set())]
    }
    cleaned_data = ChainMap({}, data)
    for key, value in cleaned_data.items():
        cleaned_data[key] = (
            _replace(value) if key.lower() in sensitive_fields else _clean_up(value, logger)
        )
    return dict(cleaned_data)


def _replace(value: Any):
    if callable(REPLACEMENT):
        replaced = REPLACEMENT(str(value).encode())
        if REPLACEMENT_TEXT.startswith("shake_"):
            return replaced.hexdigest(256)
        return replaced.hexdigest()
    return REPLACEMENT
