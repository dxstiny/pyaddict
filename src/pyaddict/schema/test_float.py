from . import Float


def test_min_inclusive() -> None:
    schema = Float().min(0.0)
    assert not schema.validate(-1.0)
    assert schema.validate(0.0)
    assert schema.validate(5.0)


def test_min_exclusive() -> None:
    schema = Float().min(0, inclusive=False)
    assert not schema.validate(-1.0)
    assert not schema.validate(0.0)
    assert schema.validate(1.0)
    assert schema.validate(5.0)


def test_max_inclusive() -> None:
    schema = Float().max(10.0)
    assert not schema.validate(11.0)
    assert schema.validate(10.0)
    assert schema.validate(5.0)


def test_max_exclusive() -> None:
    schema = Float().max(10.0, inclusive=False)
    assert not schema.validate(11.0)
    assert not schema.validate(10.0)
    assert schema.validate(9.0)
    assert schema.validate(5.0)


def test_do_not_coerce() -> None:
    schema = Float()
    assert not schema.validate("1.0")
    assert not schema.validate({1: 0})
    assert not schema.validate([1, 0])
    assert not schema.validate((1, 0))
    assert schema.validate(1.0)
    assert not schema.validate(1)


def test_do_coerce() -> None:
    schema = Float().coerce()
    assert schema.validate("1")
    assert schema.validate("1.0")
    assert not schema.validate({1: 0})
    assert not schema.validate([1, 0])
    assert not schema.validate((1, 0))
    assert schema.validate(1.0)
    assert schema.validate(1)


def test_nullable() -> None:
    assert not Float().validate(None)
    assert Float().nullable().validate(None)
