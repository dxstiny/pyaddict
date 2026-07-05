from typing import Any, overload

from pyaddict.chain import ChainLink, traverse
from pyaddict.common import JObject


class JDict(dict):
    __slots__ = ("_data", "_chainable")

    def __init__(self, data: JObject | None = None, *, chainable: bool = False) -> None:
        self._data = data or {}
        self._chainable = chainable
        super().__init__(self._data)

    def _get_item(self, key: str, *, optional: bool = False) -> None:
        if self._chainable:
            return traverse(
                self._data, ChainLink.create_chain(key, last_optional=optional)
            )
        if optional:
            return self.get(key)
        return self[key]

    def chain(self) -> "JDict":
        self._chainable = True
        return self

    def no_chain(self) -> "JDict":
        self._chainable = False
        return self

    @overload
    def optional_get(self, key: str) -> Any | None: ...

    @overload
    def optional_get[T](self, key: str, type_: type[T], default: T) -> T: ...

    @overload
    def optional_get[T](
        self, key: str, type_: type[T], default: T | None = None
    ) -> T | None: ...

    def optional_get[T](
        self, key: str, type_: type[T] | None = None, default: T | None = None
    ) -> Any | T | None:
        value = self._get_item(key, optional=True)
        if type_ and not isinstance(value, type_):
            return default
        return value or default

    def ensure[T](self, key: str, type_: type[T], default: T | None = None) -> T:
        try:
            value = self._get_item(key)
            print(value)
            if isinstance(value, type_):
                return value
            return default or type_()
        except:  # noqa: E722
            return default or type_()

    def ensure_cast[T](self, key: str, type_: type[T], default: T | None = None) -> T:
        try:
            return type_(self._get_item(key))
        except:  # noqa: E722
            return default or type_()

    def expect[T](self, key: str, type_: type[T]) -> T:
        val = self._get_item(key)
        if not isinstance(val, type_):
            raise TypeError(f"expected {val} to be {type_}, not {type(val)}")
        return val
