import pytest

from pyaddict.jlist import JList

data = [{"name": "John", "age": 12}, {"name": "Jane", "age": 14}]


def test_no_chain() -> None:
    JList(data).expect(0, dict)
    JList(data).expect(1, dict)
    JList(data).expect("0", dict)
    with pytest.raises(IndexError):
        JList(data).expect(2, dict)
    with pytest.raises(ValueError):
        JList(data).expect("0.name", dict)


def test_chain() -> None:
    item = JList(data).chain()
    item.expect(0, dict)
    item.expect(1, dict)
    item.expect("0", dict)
    assert item.expect("[0].name", str) == data[0]["name"]
    with pytest.raises(KeyError):
        item.optional_get("0.test")
    assert item.optional_get("?.b?.d") is None
    assert item.expect("[].name", list) == [x["name"] for x in data]
