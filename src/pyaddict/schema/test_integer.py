from . import Integer


def test_min_inclusive() -> None:
    schema = Integer().min(0)
    assert not schema.validate(-1)
    assert schema.validate(0)
    assert schema.validate(5)


def test_min_exclusive() -> None:
    schema = Integer().min(0, inclusive=False)
    assert not schema.validate(-1)
    assert not schema.validate(0)
    assert schema.validate(1)
    assert schema.validate(5)


def test_max_inclusive() -> None:
    schema = Integer().max(10)
    assert not schema.validate(11)
    assert schema.validate(10)
    assert schema.validate(5)


def test_max_exclusive() -> None:
    schema = Integer().max(10, inclusive=False)
    assert not schema.validate(11)
    assert not schema.validate(10)
    assert schema.validate(9)
    assert schema.validate(5)


def test_do_not_coerce() -> None:
    schema = Integer()
    assert not schema.validate("1.0")
    assert not schema.validate({1: 0})
    assert not schema.validate([1, 0])
    assert not schema.validate((1, 0))
    assert not schema.validate(1.0)
    assert schema.validate(1)


def test_do_coerce() -> None:
    schema = Integer().coerce()
    assert schema.validate("1.0")
    assert not schema.validate({1: 0})
    assert not schema.validate([1, 0])
    assert not schema.validate((1, 0))
    assert schema.validate(1.0)
    assert schema.validate(1)


def test_nullable() -> None:
    assert not Integer().validate(None)
    assert Integer().nullable().validate(None)
