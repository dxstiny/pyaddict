from . import Array, Integer


def test_do_not_coerce() -> None:
    schema = Array()
    assert not schema.validate(None)
    assert not schema.validate("Lorem")
    assert not schema.validate({"a": 1})
    assert schema.validate([1, 2])
    assert schema.validate([])
    assert not schema.validate("[1, 2]")
    assert not schema.validate(1)
    assert not schema.validate(1.0)
    assert not schema.validate(True)


def test_do_coerce() -> None:
    schema = Array().coerce()
    assert not schema.validate(None)
    assert not schema.validate("Lorem")
    assert not schema.validate({"a": 1})
    assert schema.validate([1, 2])
    assert schema.validate("[1,2]")
    assert not schema.validate(1)
    assert not schema.validate(1.0)
    assert not schema.validate(True)


def test_length() -> None:
    schema = Array().min(2)
    assert not schema.validate([1])
    assert schema.validate([1, 2])

    schema = Array().max(2)
    assert not schema.validate([1, 2, 3])
    assert schema.validate([1, 2])


def test_all_items() -> None:
    schema = Array(Integer())
    assert not schema.validate(["1"])
    assert schema.validate([1])
    assert schema.validate([1, 2])
    assert not schema.validate([1, "2"])
    assert not schema.validate([1, None])

    schema = Array(Integer().coerce())
    assert schema.validate(["1"])
    assert schema.validate([1])
    assert schema.validate([1, 2])
    assert schema.validate([1, "2"])


def test_item_at() -> None:
    schema = Array().includes(Integer(), at_index=1)
    assert not schema.validate([])
    assert not schema.validate([1, "a"])
    assert schema.validate([1, 2])
    assert schema.validate(["a", 2])
