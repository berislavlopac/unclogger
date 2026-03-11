import hashlib
import json

import pytest

import unclogger


def _expected(value, hash_function):
    hashed = hash_function(value.encode())
    try:
        return hashed.hexdigest()
    except TypeError:
        return hashed.hexdigest(256)


@pytest.mark.parametrize("hash_algo", hashlib.algorithms_guaranteed)
def test_message_with_password_and_email_is_hashed_correctly(caplog, hash_algo, sanitary_hash):
    unclogger.processors.CUSTOM_PROCESSORS.clear()

    hash_function = getattr(hashlib, hash_algo)

    unclogger.add_processors(sanitary_hash(hash_function))
    caplog.set_level("INFO")

    message = "Test with request password"
    logger_name = __name__

    logger = unclogger.get_logger(logger_name)

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
    assert record["request"]["password"] == _expected(request["password"], hash_function)
    assert record["request"]["email"] == _expected(request["email"], hash_function)

    unclogger.processors.CUSTOM_PROCESSORS.clear()
