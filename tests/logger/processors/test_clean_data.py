import json
from decimal import Decimal

from unclogger import get_logger
from unclogger.processors import clean_sensitive_data, HIDE_TEXT


def test_example_log_message_from_auth_is_cleaned_correctly(caplog):
    caplog.set_level("INFO")

    message = """{
    "textPayload": "Response Headers: {'Authentication': 'Bearer sensitive_info_auth_token',
    'Refresh': 'sensitive_info_refresh_token'}",
    }"""
    logger_name = "test logger"

    logger = get_logger(logger_name)
    logger.info(message)

    record = json.loads(caplog.messages[0])
    assert len(record) == 4
    assert record["event"] == (
        "The content of this message has been replaced because the following keyword was detected: 'Authentication':"
    )
    assert record["level"] == "info"
    assert record["logger"] == logger_name


def test_message_with_Bearer_in_text_is_cleaned_correctly(caplog):
    caplog.set_level("INFO")

    message = """some random text 'Bearer sensitive_info_auth_token'"""
    logger_name = "test logger"

    logger = get_logger(logger_name)
    logger.info(message)

    record = json.loads(caplog.messages[0])
    assert len(record) == 4
    assert record["event"] == (
        "The content of this message has been replaced because the following keyword was detected: 'Bearer "
    )
    assert record["level"] == "info"
    assert record["logger"] == logger_name


def test_message_with_Refresh_in_text_is_cleaned_correctly(caplog):
    caplog.set_level("INFO")

    message = """{'Refresh': 'sensitive_info_refresh_token'}"""
    logger_name = "test logger"

    logger = get_logger(logger_name)
    logger.info(message)

    record = json.loads(caplog.messages[0])
    assert len(record) == 4
    assert record["event"] == (
        "The content of this message has been replaced because the following keyword was detected: 'Refresh':"
    )
    assert record["level"] == "info"
    assert record["logger"] == logger_name


def test_message_with_password_and_email_is_cleaned_correctly(caplog):
    caplog.set_level("INFO")

    message = "Test with request password"
    logger_name = "test logger"

    logger = get_logger(logger_name)
    request = {
        "email": "user@domain.xyz",
        "password": "this is a sensitive value",
    }

    logger.info(message, request=request)

    record = json.loads(caplog.messages[0])
    assert len(record) == 5
    assert record["event"] == "Test with request password"
    assert record["level"] == "info"
    assert record["logger"] == logger_name
    assert record["request"]["password"] == HIDE_TEXT
    assert record["request"]["email"] == HIDE_TEXT


def test_message_with_password_and_email_in_event_is_cleaned_correctly(caplog):
    caplog.set_level("INFO")

    logger_name = "test logger"
    message = {
        "email": "user@domain.xyz",
        "password": "this is a sensitive value",
    }

    logger = get_logger(logger_name)
    logger.info(message)

    record = json.loads(caplog.messages[0])
    assert len(record) == 4
    assert record["level"] == "info"
    assert record["logger"] == logger_name
    assert record["event"]["password"] == HIDE_TEXT
    assert record["event"]["email"] == HIDE_TEXT


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
    assert cleaned_event_dict["email"] is HIDE_TEXT
    assert cleaned_event_dict["password"] is HIDE_TEXT
    assert cleaned_event_dict["parameters"]["body"]["email"] is HIDE_TEXT
    assert cleaned_event_dict["parameters"]["body"]["password"] is HIDE_TEXT
    assert cleaned_event_dict["as_list"][0]["firstName"] is HIDE_TEXT
    assert cleaned_event_dict["as_list"][0]["lastName"] is HIDE_TEXT
    assert cleaned_event_dict["as_list"][1]["firstName"] is HIDE_TEXT
    assert cleaned_event_dict["as_list"][1]["lastName"] is HIDE_TEXT
    assert cleaned_event_dict["context"]["email"] is HIDE_TEXT
    assert cleaned_event_dict["response"]["auth"] is HIDE_TEXT
    assert cleaned_event_dict["response"]["refresh"] is HIDE_TEXT
    assert cleaned_event_dict["response"]["email_1"] is HIDE_TEXT
    assert cleaned_event_dict["Authentication"] is HIDE_TEXT

    assert cleaned_event_dict != event_dict


def test_log_object_in_event_is_cleaned_correctly():
    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "request_type": "http",
        "event": "some random text 'Bearer sensitive_info_auth_token'",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert cleaned_event_dict["event"] == (
        "The content of this message has been replaced because the following keyword was detected: 'Bearer "
    )
    assert event_dict != cleaned_event_dict


def test_textual_value_is_cleaned_correctly():
    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "str_field": "Bearer sensitive_info_auth_token",
        "event": "some random text",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert cleaned_event_dict["str_field"] == (
        "The content of this message has been replaced because the following keyword was detected: Bearer "
    )


def test_list_value_is_cleaned_correctly():
    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "list_field": ("http", "Bearer sensitive_info_auth_token", "blabla"),
        "event": "some random text",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert cleaned_event_dict["list_field"] == [
        "http",
        "The content of this message has been replaced because the following keyword was detected: Bearer ",
        "blabla",
    ]


def test_dict_value_is_cleaned_correctly():
    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "dict_field": {"a": "http", "b": "Bearer sensitive_info_auth_token", "c": "blabla"},
        "event": "some random text",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert cleaned_event_dict["dict_field"] == {
        "a": "http",
        "b": "The content of this message has been replaced because the following keyword was detected: Bearer ",
        "c": "blabla",
    }


def test_tuple_value_is_cleaned_correctly():
    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "tuple_field": ("http", "Bearer sensitive_info_auth_token", "blabla"),
        "event": "some random text",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert cleaned_event_dict["tuple_field"] == [
        "http",
        "The content of this message has been replaced because the following keyword was detected: Bearer ",
        "blabla",
    ]


def test_set_value_is_cleaned_correctly():
    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "set_field": {"http", "Bearer sensitive_info_auth_token", "blabla"},
        "event": "some random text",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert sorted(cleaned_event_dict["set_field"]) == [
        "The content of this message has been replaced because the following keyword was detected: Bearer ",
        "blabla",
        "http",
    ]


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


def test_generic_object_with_custom_text_is_cleaned_correctly():
    class Foo:
        def __str__(self):
            return "Bearer sensitive_info_auth_token"

    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "object_field": Foo(),
        "event": "some random text",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert isinstance(cleaned_event_dict["object_field"], str)
    assert cleaned_event_dict["object_field"] == (
        "The content of this message has been replaced because the following keyword was detected: Bearer "
    )


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
    logger.sensitive_keys.add("illegalkey")
    logger.sensitive_keys.add("foo")

    logger.info(
        "clean sensitive keys with dict",
        context_id="cxt_fe76c000000000000000000_0000000000000",
        illegalKey="blabla",
    )

    record = json.loads(caplog.messages[0])
    assert record["illegalKey"] == HIDE_TEXT
    assert record["context_id"] == "cxt_fe76c000000000000000000_0000000000000"


def test_setting_custom_sensitive_keywords_on_runtime_cleans_output_correctly(caplog):
    logger = get_logger("test logger")
    logger.sensitive_keys = {"illegalkey", "foo"}

    logger.info(
        "clean sensitive keys with dict",
        context_id="cxt_fe76c000000000000000000_0000000000000",
        illegalKey="blabla",
    )

    record = json.loads(caplog.messages[0])
    assert record["illegalKey"] == HIDE_TEXT
    assert record["context_id"] == "cxt_fe76c000000000000000000_0000000000000"


def test_changing_custom_sensitive_keywords_on_runtime_cleans_output_correctly(caplog):
    logger = get_logger("test logger")
    payload = {"foo": "1234", "bar": "5678", "fooBar": "9876"}

    logger.sensitive_keys = {"FOO", "bar"}
    logger.info("clean sensitive keys with dict", payload=payload)
    record = json.loads(caplog.messages[0])

    assert record["payload"]["foo"] == HIDE_TEXT
    assert record["payload"]["bar"] == HIDE_TEXT
    assert record["payload"]["fooBar"] != HIDE_TEXT

    logger.sensitive_keys.add("fooBar")
    logger.info("clean sensitive keys with dict", payload=payload)
    fully_cleaned_record = json.loads(caplog.messages[1])

    assert fully_cleaned_record["payload"]["foo"] == HIDE_TEXT
    assert fully_cleaned_record["payload"]["bar"] == HIDE_TEXT
    assert fully_cleaned_record["payload"]["fooBar"] == HIDE_TEXT
