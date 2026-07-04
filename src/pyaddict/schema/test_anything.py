from . import Anything


def test_any() -> None:
    schema = Anything()
    assert schema.validate(None)
    assert schema.validate("Lorem")
    assert schema.validate({"a": 1})
    assert schema.validate([1, 2])
    assert schema.validate(1)
    assert schema.validate(1.0)
    assert schema.validate(True)
