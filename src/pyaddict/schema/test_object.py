from . import Integer, Object, String


def test_do_not_coerce() -> None:
    schema = Object(additional_properties=True)
    assert not schema.validate(None)
    assert not schema.validate("Lorem")
    assert schema.validate({"a": 1})
    assert schema.validate({})
    assert not schema.validate([1, 2])
    assert not schema.validate("[1, 2]")
    assert not schema.validate(1)
    assert not schema.validate(1.0)
    assert not schema.validate(True)


def test_do_coerce() -> None:
    schema = Object(additional_properties=True).coerce()
    assert not schema.validate(None)
    assert not schema.validate("Lorem")
    assert schema.validate({"a": 1})
    assert schema.validate('{"a": 1}')
    assert schema.validate({})
    assert not schema.validate([1, 2])
    assert not schema.validate("[1, 2]")
    assert not schema.validate(1)
    assert not schema.validate(1.0)
    assert not schema.validate(True)


def test_additional_properties() -> None:
    schema = Object()
    assert not schema.validate({"1": 2})
    assert schema.validate({})


def test_items() -> None:
    schema = Object({"1": 2, "optional": Integer().optional()})
    assert not schema.validate({})
    assert schema.validate({"1": 2})
    assert not schema.validate({"1": 2, "optional": None})
    assert schema.validate({"1": 2, "optional": 5})


def test_default_items() -> None:
    schema = Object({"default": String().nullable().optional().default("value")})
    assert schema.validate({})
    assert schema.validate({}).unwrap()["default"] == "value"
    assert schema.validate({"default": None})
    assert schema.validate({"default": None}).unwrap()["default"] == "value"
    assert schema.validate({"default": "something"})
    assert schema.validate({"default": "something"}).unwrap()["default"] == "something"


def test_modify_schema() -> None:
    schema = Object({"first": "schema"})
    assert schema.validate({"first": "schema"})
    assert schema["first"] == "schema"
    schema["first"] = Integer()
    assert not schema.validate({"first": "schema"})
    assert schema.validate({"first": 1})
    schema["second"] = Integer()
    assert not schema.validate({"first": 1})
    assert schema.validate({"first": 1, "second": 2})
