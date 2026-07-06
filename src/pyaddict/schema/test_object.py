from . import AnyObject, Integer, Object, String


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


def test_any_object() -> None:
    schema = AnyObject()
    assert schema.validate({})
    assert not schema.validate(None)
    assert not schema.validate(5)
    assert schema.validate({"test": "value"})


def test_static() -> None:
    schema = Object({"1": 1, "null": None, "test": "test"})
    assert schema.validate({"1": 1, "null": None, "test": "test"})
    assert not schema.validate({"1": "1", "null": None, "test": "test"})
    assert not schema.validate({"1": 1, "null": "None", "test": "test"})
    assert not schema.validate({"1": 1, "null": None, "test": 5})


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


def test_unwrapped_value() -> None:
    schema = Object(
        {"name": String().optional().nullable().default("Alex")},
        additional_properties=True,
    )
    result = schema.validate({"age": 5})
    assert result

    data = result.unwrap()
    assert isinstance(data, dict)
    assert data["name"] == "Alex"
    assert data["age"] == 5

    result = schema.validate({"name": None, "age": 5})
    assert result

    data = result.unwrap()
    assert isinstance(data, dict)
    assert data["name"] == "Alex"
    assert data["age"] == 5
