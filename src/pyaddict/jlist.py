from typing import Any, overload

from pyaddict.chain import ChainLink, traverse
from pyaddict.common import JArray


class JList(list):
    __slots__ = ("_data", "_chainable")

    def __init__(self, data: JArray | None = None, *, chainable: bool = False) -> None:
        self._data = data or {}
        self._chainable = chainable
        super().__init__(self._data)

    def _get_item(self, key: int | str) -> None:
        if self._chainable:
            return traverse(
                self._data, ChainLink.create_chain(str(key), allow_first_int=True)
            )
        return self._data[int(key)]

    def chain(self) -> "JList":
        self._chainable = True
        return self

    def no_chain(self) -> "JList":
        self._chainable = False
        return self

    @overload
    def optional_get(self, key: int | str) -> Any | None: ...

    @overload
    def optional_get[T](self, key: int | str, type_: type[T], default: T) -> T: ...

    @overload
    def optional_get[T](
        self, key: int | str, type_: type[T], default: T | None = None
    ) -> T | None: ...

    def optional_get[T](
        self, key: int | str, type_: type[T] | None = None, default: T | None = None
    ) -> T | None:
        value = self._get_item(key)
        if type_ and isinstance(value, type_):
            return value or default
        return value or default

    def ensure[T](self, key: int | str, type_: type[T], default: T | None = None) -> T:
        try:
            value = self._get_item(key)
            if isinstance(value, type_):
                return value
            return default or type_()
        except:  # noqa: E722
            return default or type_()

    def ensure_cast[T](
        self, key: int | str, type_: type[T], default: T | None = None
    ) -> T:
        try:
            return type_(self._get_item(key))
        except:  # noqa: E722
            return default or type_()

    def expect[T](self, key: int | str, type_: type[T]) -> T:
        val = self._get_item(key)
        assert isinstance(val, type_)
        return val
