from uuid import uuid4

import pytest

import unclogger


@pytest.fixture
def custom_processor():
    def wrapper(proc_id=None):
        if proc_id is None:
            proc_id = str(uuid4())

        def _proc(logger, name, event_dict):
            event_dict["custom_processor_id"] = proc_id
            return event_dict

        return _proc

    return wrapper


def test_custom_processors_are_added_to_configuration(custom_processor):
    custom_1 = custom_processor(1)
    custom_2 = custom_processor(2)

    previous_processors_count = len(unclogger.processors.CUSTOM_PROCESSORS)

    unclogger.add_processors(custom_1, custom_2)

    assert len(unclogger.processors.CUSTOM_PROCESSORS) == previous_processors_count + 2
    assert custom_1 in unclogger.processors.CUSTOM_PROCESSORS
    assert custom_2 in unclogger.processors.CUSTOM_PROCESSORS

    unclogger.processors.CUSTOM_PROCESSORS.clear()


def test_custom_processors_are_added_to_configuration_only_once(custom_processor):
    custom_1 = custom_processor(1)
    custom_2 = custom_processor(2)

    previous_processors_count = len(unclogger.processors.CUSTOM_PROCESSORS)

    unclogger.add_processors(custom_1, custom_2, custom_1)

    assert len(unclogger.processors.CUSTOM_PROCESSORS) == previous_processors_count + 2
    assert custom_1 in unclogger.processors.CUSTOM_PROCESSORS
    assert custom_2 in unclogger.processors.CUSTOM_PROCESSORS

    unclogger.processors.CUSTOM_PROCESSORS.clear()
