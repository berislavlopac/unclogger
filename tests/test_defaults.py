import uuid
from datetime import date, datetime, timezone

from unclogger.defaults import json_default


def test_json_default_formats_date_correctly():
    example_date = date(2002, 5, 22)
    assert json_default(example_date) == "2002-05-22"


def test_json_default_formats_datetime_correctly():
    example_date = datetime(2008, 5, 5, hour=11, minute=45, tzinfo=timezone.utc)
    assert json_default(example_date) == "2008-05-05T11:45:00+00:00Z"


def test_json_default_correctly_formats_UUID():
    example_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, "lopac.net")
    assert json_default(example_uuid) == "5e451eaa-4c0e-5590-8d96-adbf44434374"


def test_json_default_formats_a_generic_object_correctly():
    class Foo:
        def __init__(self):
            self.bar = "baz"
            self.abc = 123

        def __repr__(self):
            return f"bar={self.bar}, abc={self.abc}"

    example_object = Foo()
    assert json_default(example_object) == "bar=baz, abc=123"
