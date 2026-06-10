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


def test_custom_processors_run_in_registration_order(custom_processor):
    execution_order = []

    def recorder(proc_id):
        def _proc(logger, name, event_dict):
            execution_order.append(proc_id)
            return event_dict

        return _proc

    unclogger.processors.CUSTOM_PROCESSORS.clear()
    # Register more than a couple so the test would fail on a hash-ordered set.
    processors = [recorder(i) for i in range(5)]
    unclogger.add_processors(*processors)

    unclogger.processors.run_custom_processors(None, "info", {})

    assert execution_order == [0, 1, 2, 3, 4]

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
