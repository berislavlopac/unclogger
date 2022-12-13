import json
from decimal import Decimal

from unclogger import get_logger
from unclogger.processors.clean_data import clean_sensitive_data, DEFAULT_REPLACEMENT


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
    assert (
        record["event"]
        == "#### WARNING: Log message replaced due to sensitive keyword: 'Authentication':"
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
    assert (
        record["event"] == "#### WARNING: Log message replaced due to sensitive keyword: 'Bearer "
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
    assert (
        record["event"] == "#### WARNING: Log message replaced due to sensitive keyword: 'Refresh':"
    )
    assert record["level"] == "info"
    assert record["logger"] == logger_name


def test_log_object_in_event_is_cleaned_correctly():
    event_dict = {
        "context_id": "cxt_fe76c000000000000000000_0000000000000",
        "request_type": "http",
        "event": "some random text 'Bearer sensitive_info_auth_token'",
    }

    cleaned_event_dict = clean_sensitive_data(None, "", event_dict)

    assert cleaned_event_dict["event"] == (
        "#### WARNING: Log message replaced due to sensitive keyword: 'Bearer "
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
        "#### WARNING: Log message replaced due to sensitive keyword: Bearer "
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
        "#### WARNING: Log message replaced due to sensitive keyword: Bearer ",
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
        "b": "#### WARNING: Log message replaced due to sensitive keyword: Bearer ",
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
        "#### WARNING: Log message replaced due to sensitive keyword: Bearer ",
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
        "#### WARNING: Log message replaced due to sensitive keyword: Bearer ",
        "blabla",
        "http",
    ]


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
        "#### WARNING: Log message replaced due to sensitive keyword: Bearer "
    )
