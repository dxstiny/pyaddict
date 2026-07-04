import pytest

from pyaddict.jdict import JDict

data = {"a": {"b": [{"c": 1}, {"c": 2}]}}


def test_no_chain() -> None:
    JDict(data).expect("a", dict)
    with pytest.raises(KeyError):
        JDict(data).expect("b", dict)
    with pytest.raises(KeyError):
        JDict(data).expect("a.b", dict)
    with pytest.raises(TypeError):
        JDict(data).expect("a", list)


def test_chain() -> None:
    JDict(data).chain().expect("a", dict)
    JDict(data).chain().expect("a.b", list)
    assert JDict(data).chain().expect("a.b[0].c", int) == 1
    assert JDict(data).chain().expect("a.b[].c", list) == [1, 2]
    with pytest.raises(KeyError):
        JDict(data).chain().optional_get("b.d")
    assert JDict(data).chain().optional_get("b?.d") is None
