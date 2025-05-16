import json
from decimal import Decimal

from unclogger import get_logger
from unclogger.processors.clean_data import DEFAULT_REPLACEMENT, clean_sensitive_data


def test_message_with_password_and_email_is_cleaned_correctly(caplog):
    caplog.set_level("INFO")

    message = "Test with request password"
    logger_name = "test logger"

    logger = get_logger(logger_name)
    request = {"Email": "user@domain.xyz", "password": "this is a sensitive value"}

    logger.info(message, request=request)

    record = json.loads(caplog.messages[0])
    assert len(record) == 5
    assert record["event"] == "Test with request password"
    assert record["level"] == "info"
    assert record["logger"] == logger_name
    assert record["request"]["password"] == DEFAULT_REPLACEMENT
    assert record["request"]["Email"] == DEFAULT_REPLACEMENT


def test_message_with_password_and_email_in_event_is_cleaned_correctly(caplog):
    caplog.set_level("INFO")

    logger_name = "test logger"
    message = {"email": "user@domain.xyz", "password": "this is a sensitive value"}

    logger = get_logger(logger_name)
    logger.info(message)

    record = json.loads(caplog.messages[0])
    assert len(record) == 4
    assert record["level"] == "info"
    assert record["logger"] == logger_name
    assert record["event"]["password"] == DEFAULT_REPLACEMENT
    assert record["event"]["email"] == DEFAULT_REPLACEMENT


def test_complex_log_object_is_cleaned_correctly():
    event_dict = {
        "context": {"email": "sensitive@email.address"},
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "parameters": {
            "context": {"callerUserId": None},
            "body": {"email": "sensitive@email.address", "password": "sensitive_password"},
        },
        "response": {
            "status": "OK",
            "auth": "eyJra...",
            "refresh": "eyJjd...",
            "email_1": "user@domain",
        },
        "Authentication": "eyJra...",
        "request_type": "http",
        "email": "sensitive@email.address",
        "password": "sensitive_value",
        "calling_user_type": "service",
        "event": "Request",
        "logger": "service_function.common.cloud_function",
        "level": "info",
        "timestamp": "2021-01-01T00:00:00.000000Z",
        "as_list": [
            {
                "firstName": "Sensitive First Name",
                "lastName": "Sensitive Last Name",
                "callerUserId": "000000000000",
            },
            {
                "firstName": "Sensitive First Name",
                "lastName": "Sensitive Last Name",
                "callerUserId": "000000000000",
            },
        ],
        "another_list": ["1", "2"],
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert cleaned_event_dict is not None
    assert cleaned_event_dict["email"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["password"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["parameters"]["body"]["email"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["parameters"]["body"]["password"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["as_list"][0]["firstName"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["as_list"][0]["lastName"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["as_list"][1]["firstName"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["as_list"][1]["lastName"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["context"]["email"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["response"]["auth"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["response"]["refresh"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["response"]["email_1"] is DEFAULT_REPLACEMENT
    assert cleaned_event_dict["Authentication"] is DEFAULT_REPLACEMENT

    assert cleaned_event_dict != event_dict


def test_numeric_values_are_cleaned_correctly():
    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "int_field": 123,
        "float_field": 123.45,
        "event": "some random text",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert cleaned_event_dict["int_field"] == 123
    assert cleaned_event_dict["float_field"] == 123.45


def test_decimal_value_is_cleaned_correctly():
    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "decimal_field": Decimal("123.45"),
        "event": "some random text",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert cleaned_event_dict["decimal_field"] == 123.45


def test_generic_object_is_cleaned_correctly():
    class Foo:
        foo = "Bearer sensitive_info_auth_token"

    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "object_field": Foo(),
        "event": "some random text",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert isinstance(cleaned_event_dict["object_field"], str)
    assert "Bearer " not in cleaned_event_dict["object_field"]
    assert ".Foo object at " in cleaned_event_dict["object_field"]


def test_adding_custom_sensitive_keywords_on_runtime_cleans_output_correctly(caplog):
    logger = get_logger("test logger")
    logger.config.sensitive_keys = {"illegalkey", "foo"}

    logger.info(
        "clean sensitive keys with dict",
        context_id="cxt_fe76c000000000000000000_0000000000000",
        illegalKey="blabla",
    )

    record = json.loads(caplog.messages[0])
    assert record["illegalKey"] == DEFAULT_REPLACEMENT
    assert record["context_id"] == "cxt_fe76c000000000000000000_0000000000000"


def test_setting_custom_sensitive_keywords_on_runtime_cleans_output_correctly(caplog):
    logger = get_logger("test logger")
    logger.config.sensitive_keys = {"illegalkey", "foo"}

    logger.info(
        "clean sensitive keys with dict",
        context_id="cxt_fe76c000000000000000000_0000000000000",
        illegalKey="blabla",
    )

    record = json.loads(caplog.messages[0])
    assert record["illegalKey"] == DEFAULT_REPLACEMENT
    assert record["context_id"] == "cxt_fe76c000000000000000000_0000000000000"


def test_changing_custom_sensitive_keywords_on_runtime_cleans_output_correctly(caplog):
    logger = get_logger("test logger")
    payload = {"foo": "1234", "bar": "5678", "fooBar": "9876"}

    logger.config.sensitive_keys = {"FOO", "bar"}
    logger.info("clean sensitive keys with dict", payload=payload)
    record = json.loads(caplog.messages[0])

    assert record["payload"]["foo"] == DEFAULT_REPLACEMENT
    assert record["payload"]["bar"] == DEFAULT_REPLACEMENT
    assert record["payload"]["fooBar"] != DEFAULT_REPLACEMENT

    logger.config.sensitive_keys.add("fooBar")
    logger.info("clean sensitive keys with dict", payload=payload)
    fully_cleaned_record = json.loads(caplog.messages[1])

    assert fully_cleaned_record["payload"]["foo"] == DEFAULT_REPLACEMENT
    assert fully_cleaned_record["payload"]["bar"] == DEFAULT_REPLACEMENT
    assert fully_cleaned_record["payload"]["fooBar"] == DEFAULT_REPLACEMENT
