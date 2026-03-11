import json

import unclogger

message_replacement_part = "Log message replaced"


def test_message_with_password_and_email_is_cleaned_correctly(caplog, sanitary_replacement):
    unclogger.add_processors(sanitary_replacement)
    field_replacement = sanitary_replacement.replacement

    caplog.set_level("INFO")

    message = "Test with request password"
    logger_name = "test logger"

    logger = unclogger.get_logger(logger_name)
    request = {"Email": "user@domain.xyz", "password": "this is a sensitive value"}

    logger.info(message, request=request)

    record = json.loads(caplog.messages[0])
    assert len(record) == 5
    assert record["event"] == "Test with request password"
    assert record["level"] == "info"
    assert record["logger"] == logger_name
    assert record["request"]["password"] == field_replacement
    assert record["request"]["Email"] == field_replacement

    unclogger.processors.CUSTOM_PROCESSORS.clear()


def test_message_with_password_and_email_in_event_is_cleaned_correctly(
    caplog, sanitary_replacement
):
    unclogger.add_processors(sanitary_replacement)

    caplog.set_level("INFO")

    logger_name = "test logger"
    message = {"email": "user@domain.xyz", "password": "this is a sensitive value"}

    logger = unclogger.get_logger(logger_name)
    logger.info(message)

    record = json.loads(caplog.messages[0])
    assert len(record) == 4
    assert record["level"] == "info"
    assert record["logger"] == logger_name
    assert record["event"]["password"] == sanitary_replacement.replacement
    assert record["event"]["email"] == sanitary_replacement.replacement

    unclogger.processors.CUSTOM_PROCESSORS.clear()


def _test_adding_custom_sensitive_keywords_on_runtime_cleans_output_correctly(
    caplog, sanitary_processor
):
    unclogger.add_processors(sanitary_processor)

    logger = unclogger.get_logger("test logger")
    logger.config.sensitive_keys = {"illegalkey", "foo"}

    logger.info(
        "clean sensitive keys with dict",
        context_id="cxt_fe76c000000000000000000_0000000000000",
        illegalKey="blabla",
    )

    record = json.loads(caplog.messages[0])
    assert record["illegalKey"] == message_replacement_part
    assert record["context_id"] == "cxt_fe76c000000000000000000_0000000000000"

    logger.config.sensitive_keys = {}

    unclogger.processors.CUSTOM_PROCESSORS.clear()


def _test_setting_custom_sensitive_keywords_on_runtime_cleans_output_correctly(caplog):
    logger = unclogger.get_logger("test logger")
    logger.config.sensitive_keys = {"illegalkey", "foo"}

    logger.info(
        "clean sensitive keys with dict",
        context_id="cxt_fe76c000000000000000000_0000000000000",
        illegalKey="blabla",
    )

    record = json.loads(caplog.messages[0])
    assert message_replacement_part in record["illegalKey"]
    assert record["context_id"] == "cxt_fe76c000000000000000000_0000000000000"

    logger.config.sensitive_keys = {}


def _test_changing_custom_sensitive_keywords_on_runtime_cleans_output_correctly(caplog):
    logger = unclogger.get_logger("test logger")
    payload = {"foo": "1234", "bar": "5678", "fooBar": "9876"}

    logger.config.sensitive_keys = {"FOO", "bar"}
    logger.info("clean sensitive keys with dict", payload=payload)
    record = json.loads(caplog.messages[0])

    assert message_replacement_part in record["payload"]["foo"]
    assert message_replacement_part in record["payload"]["bar"]
    assert message_replacement_part in record["payload"]["fooBar"]

    logger.config.sensitive_keys.add("fooBar")
    logger.info("clean sensitive keys with dict", payload=payload)
    fully_cleaned_record = json.loads(caplog.messages[1])

    assert message_replacement_part in fully_cleaned_record["payload"]["foo"]
    assert message_replacement_part in fully_cleaned_record["payload"]["bar"]
    assert message_replacement_part in fully_cleaned_record["payload"]["fooBar"]

    logger.config.sensitive_keys = {}
