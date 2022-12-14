import hashlib
import json

import pytest

from unclogger import get_logger


def _expected(value, hash_algo):
    hash_function = getattr(hashlib, hash_algo)
    hashed = hash_function(value.encode())
    try:
        return hashed.hexdigest()
    except TypeError:
        return hashed.hexdigest(256)


@pytest.mark.parametrize("hash_algo", hashlib.algorithms_guaranteed)
def test_message_with_password_and_email_is_hashed_correctly(caplog, monkeypatch, hash_algo):
    caplog.set_level("INFO")

    message = "Test with request password"
    logger_name = "test logger"

    logger = get_logger(logger_name)
    logger.config.replacement = getattr(hashlib, hash_algo)

    request = {
        "email": "user@domain.xyz",
        "password": "this is a sensitive value",
        "safe_value": "this is not sensitive",
    }
    logger.info(message, request=request)

    record = json.loads(caplog.messages[0])
    assert len(record) == 5
    assert record["event"] == "Test with request password"
    assert record["level"] == "info"
    assert record["logger"] == logger_name
    assert record["request"]["safe_value"] == request["safe_value"]
    assert record["request"]["password"] == _expected(request["password"], hash_algo)
    assert record["request"]["email"] == _expected(request["email"], hash_algo)
