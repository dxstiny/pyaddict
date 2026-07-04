from . import Boolean, Integer, OneOf


def test_one_of() -> None:
    schema = OneOf(Boolean(), Integer())
    assert schema.validate(True)
    assert schema.validate(1)
    assert not schema.validate(None)
    assert not schema.validate({"a": 1})
    assert not schema.validate([1, 2])
    assert not schema.validate(1.0)
