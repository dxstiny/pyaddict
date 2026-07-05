import pytest

from pyaddict import JDict, JList
from pyaddict.schema import Anything, Array, Integer, Object, OneOf, String


def test_jdict() -> None:

    data = {
        "name": "John",
        "age": 30,
        "cars": [
            {"model": "BMW 230", "mpg": 27.5},
            {"model": "Ford Edge", "mpg": 24.1},
        ],
    }

    jdict = JDict(data).chain()  # enable chaining

    assert jdict.expect("name", str) == "John"
    with pytest.raises(TypeError):
        jdict.expect("name", int)  # TypeError: name is str, not int
    with pytest.raises(KeyError):
        jdict.expect("address", str)  # KeyError: key 'address' not found
    assert jdict.expect("cars[0].mpg", float) == 27.5

    # if we prefer None
    assert jdict.optional_get("name", str) == "John"
    assert jdict.optional_get("name", int) is None
    assert jdict.optional_get("address", str) is None
    with pytest.raises(KeyError):
        jdict.optional_get("address.street", str)  # KeyError: address not found
    assert jdict.optional_get("address?.street", str) is None
    with pytest.raises(IndexError):
        jdict.optional_get("cars[2].mpg", str)  # IndexError: out of range
    assert jdict.optional_get("cars[2]?.mpg", str) is None

    # if we don't care whether it exists or not
    assert jdict.ensure("name", str) == "John"
    assert jdict.ensure("name", int) == 0
    assert jdict.ensure("age", int) == 30
    assert jdict.ensure("age", str) == ""
    assert jdict.ensure("address", str, "moon") == "moon"
    assert jdict.ensure("cars[].model", list) == ["BMW 230", "Ford Edge"]
    assert jdict.ensure("cars[0].mpg", float) == 27.5
    assert jdict.ensure("cars[0].mpg", int) == 0

    # or cast to the desired type
    assert jdict.ensure_cast("cars[0].mpg", int) == 27


def test_jlist() -> None:
    data = [{"name": "John", "age": 20}, {"name": "Jane", "age": 22}]
    jlist = JList(data)

    assert jlist.expect(0, dict) == {"name": "John", "age": 20}
    with pytest.raises(TypeError):
        jlist.expect(0, int)  # TypeError: item is dict, not int
    with pytest.raises(IndexError):
        jlist.expect(2, dict)  # IndexError: out of range
    with pytest.raises(ValueError):
        jlist.expect("0.name", str)  # ValueError: invalid int

    # if we enable chaining:
    jlist = JList(data).chain()
    assert jlist.expect("0.name", str) == "John"
    assert jlist.expect("[].name", list) == ["John", "Jane"]


def test_schema() -> None:
    schema = Object(
        {
            "name": String(),
            "age": Integer().coerce(),
            "dogs": Array(OneOf(String(), Object({}, additional_properties=True)))
            .min(1)
            .optional(),
            "wildcard": Anything(),
            "valid": True,
        }
    )

    result = schema.validate(
        {"name": "John", "age": 20.0, "wildcard": [1, 2, 3], "valid": True}
    )
    assert result.valid  # True
    assert (
        result.unwrap()
    )  # { "name": "John", "age": 20, "wildcard": [1, 2, 3], "valid": True }

    result = schema.validate(
        {"name": "John", "age": 5, "dogs": 1, "wildcard": True, "valid": True}
    )
    assert not result.valid  # False
    with pytest.raises(ValueError):
        result.unwrap()  # ValueError (invalid)
    assert result.error  # 'dogs' should be list, not int
