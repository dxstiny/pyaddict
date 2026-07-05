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
    assert JDict(data).chain().optional_get("a.d") is None
    assert JDict(data).chain().optional_get("a.b.[3]?.c", int) is None


def test_ensure() -> None:
    jdata = JDict(data)
    assert jdata.ensure("a", dict)
    assert jdata.ensure("c", str) == ""
    assert jdata.ensure("c", str, "test") == "test"
    assert jdata.ensure("b", str) == ""
    assert jdata.ensure("a.b", str) == ""
    assert jdata.ensure("a.b.[0].c", str) == ""
    assert jdata.ensure("a.b.[0].c", int) == 0


def test_chain_ensure_cast() -> None:
    jdata = JDict(data).chain()
    assert jdata.ensure_cast("a", dict)
    assert jdata.ensure_cast("c", str) == ""
    assert jdata.ensure_cast("c", str, "test") == "test"
    assert jdata.ensure_cast("b", str) == ""
    assert jdata.ensure_cast("a.b[0].c", str) == "1"
    assert jdata.ensure_cast("a.b[0].c", int) == 1
    assert jdata.ensure_cast("a.b[0].c", float) == 1.0


def test_chain_ensure() -> None:
    jdata = JDict(data).chain()
    assert jdata.ensure("c", str) == ""
    assert jdata.ensure("c?.b", str) == ""
    assert jdata.ensure("c.b", str) == ""
    assert jdata.ensure("[0]", str) == ""
    assert jdata.ensure("a", dict) == data["a"]
    assert jdata.ensure("a.b.[0].c", str) == ""
    assert jdata.ensure("a.b.[0].c", int) == 1
    assert jdata.ensure("a.d", dict) == {}
    assert jdata.ensure("c?.b.d", str) == ""
    assert jdata.ensure("c?.b?.d", dict, {"a": "b"}) == {"a": "b"}
    assert jdata.ensure("c.b?.d", str) == ""


def test_optional_get() -> None:
    jdata = JDict(data)
    assert jdata.optional_get("a", dict)
    assert jdata.optional_get("c", str) is None
    assert jdata.optional_get("b", str) is None
    assert jdata.optional_get("a.b", str) is None


def test_chain_optional_get() -> None:
    jdata = JDict(data).chain()
    assert jdata.optional_get("c", str) is None
    assert jdata.optional_get("c?.b", str) is None
    with pytest.raises(KeyError):
        assert jdata.optional_get("c.b", str) is None
    assert jdata.optional_get("[0]", str) is None
    assert jdata.optional_get("a", dict)
    assert jdata.optional_get("a.d", dict) is None
    assert jdata.optional_get("c?.b.d", str) is None
    assert jdata.optional_get("c?.b?.d", dict) is None
    with pytest.raises(KeyError):
        assert jdata.optional_get("c.b?.d", str) is None


def test_expect() -> None:
    jdata = JDict(data)
    assert jdata.expect("a", dict)
    with pytest.raises(KeyError):
        assert jdata.expect("c", str) is None
    with pytest.raises(KeyError):
        assert jdata.expect("b", str) is None
    with pytest.raises(KeyError):
        assert jdata.expect("a.b", str) is None


def test_chain_expect() -> None:
    jdata = JDict(data).chain()
    with pytest.raises(KeyError):
        assert jdata.expect("c", str)
    with pytest.raises(TypeError):
        assert jdata.expect("c?.b", str) is None
    with pytest.raises(KeyError):
        assert jdata.expect("c.b", str) is None
    with pytest.raises(KeyError):
        assert jdata.expect("[0]", str) is None
    assert jdata.expect("a", dict)
    with pytest.raises(TypeError):
        assert jdata.expect("a", str)
    with pytest.raises(KeyError):
        assert jdata.expect("a.d", dict) is None
    with pytest.raises(TypeError):
        assert jdata.expect("c?.b.d", str) is None
    with pytest.raises(TypeError):
        assert jdata.expect("c?.b?.d", dict) is None
    with pytest.raises(KeyError):
        assert jdata.expect("c.b?.d", str) is None
