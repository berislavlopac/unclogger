import re

import pytest
from sanitary import StructlogSanitizer

SENSITIVE_KEYS = [
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
SENSITIVE_PATTERNS = [
    """'Authentication':""",
    """"Authentication":""",
    """'Refresh':""",
    """"Refresh":""",
    """'Bearer """,
    """"Bearer """,
    "Bearer ",
]
REPLACEMENT_MESSAGE = "#### WARNING: Log message replaced due to sensitive keyword: "


@pytest.fixture
def sanitary_replacement():
    return StructlogSanitizer(
        keys=SENSITIVE_KEYS,
        patterns=map(re.compile, SENSITIVE_PATTERNS),
        message=REPLACEMENT_MESSAGE,
    )


@pytest.fixture
def sanitary_hash():
    def get_processor(hash_function):
        return StructlogSanitizer(
            keys=SENSITIVE_KEYS,
            patterns=map(re.compile, SENSITIVE_PATTERNS),
            replacement=hash_function,
        )

    return get_processor
