from . import String


def test_min_inclusive() -> None:
    schema = String().min(1)
    assert not schema.validate("")
    assert schema.validate(" ")
    assert schema.validate("Lorem")


def test_min_exclusive() -> None:
    schema = String().min(1, inclusive=False)
    assert not schema.validate("")
    assert not schema.validate(" ")
    assert schema.validate("Hi")
    assert schema.validate("Lorem")


def test_max_inclusive() -> None:
    schema = String().max(3)
    assert not schema.validate("Hello")
    assert schema.validate("")
    assert schema.validate(" ")


def test_max_exclusive() -> None:
    schema = String().max(3, inclusive=False)
    assert not schema.validate("123")
    assert not schema.validate("Hello")
    assert schema.validate("")
    assert schema.validate(" ")


def test_do_not_coerce() -> None:
    schema = String()
    assert schema.validate("1.0")
    assert not schema.validate({1: 0})
    assert not schema.validate([1, 0])
    assert not schema.validate((1, 0))
    assert not schema.validate(1.0)
    assert not schema.validate(1)


def test_do_coerce() -> None:
    schema = String().coerce()
    assert schema.validate("1.0")
    assert not schema.validate({1: 0})
    assert not schema.validate([1, 0])
    assert not schema.validate((1, 0))
    assert schema.validate(1.0)
    assert schema.validate(1)


def test_nullable() -> None:
    assert not String().validate(None)
    assert String().nullable().validate(None)


def test_enum() -> None:
    schema = String().enum("apple", "banana")
    assert schema.validate("apple")
    assert schema.validate("banana")
    assert not schema.validate(None)
    assert not schema.validate("hello")


def test_nullable_enum() -> None:
    schema = String().nullable().enum("apple", "banana", None)
    assert schema.validate("apple")
    assert schema.validate("banana")
    assert schema.validate(None)
    assert not schema.validate("hello")


def test_regex_email() -> None:
    schema = String().email()
    assert schema.validate("mail@example.com")
    assert not schema.validate("apple")
    assert not schema.validate("https://google.com")


def test_regex_url() -> None:
    schema = String().url()
    assert not schema.validate("mail@example.com")
    assert not schema.validate("apple")
    assert schema.validate("https://google.com")
