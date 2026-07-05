"""type-safe dictionary helper."""

from typing import Any, overload

from pyaddict.chain import ChainLink, traverse
from pyaddict.common import JObject


class JDict(dict):

    """Type-safe dict helper."""

    __slots__ = ("_data", "_chainable")

    def __init__(self, data: JObject | None = None, *, chainable: bool = False) -> None:
        """Create a new type-safe dict helper."""
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
        """
        Enable chaining.

        Returns:
            self

        """
        self._chainable = True
        return self

    def no_chain(self) -> "JDict":
        """
        Disable chaining.

        Returns:
            self

        """
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
        """
        Get the value if it matches the target type.

        Returns:
            value at path: if value found and has the expected type.
            default: if value not found or not the expected type.
            None: if value not found and no default provided.

        Raises:
            KeyError: if chaining is enabled and the key
                (unless it is optional or the last one) cannot be found.
            IndexError: if chaining is enabled and the index
                (unless it is optional or the last one) is out of range.
            TypeError: if chaining is enabled and a list is indexed with a string

        """
        value = self._get_item(key, optional=True)
        if type_ and not isinstance(value, type_):
            return default
        return value or default

    def ensure[T](self, key: str, type_: type[T], default: T | None = None) -> T:
        """
        Get the value if it matches the target type.

        Returns:
            value at path: if value found and has the expected type.
            default: if value not found or not the expected type.
            type(): if value not found and no default provided.

        """
        try:
            value = self._get_item(key)
            print(value)
            if isinstance(value, type_):
                return value
            return default or type_()
        except:  # noqa: E722
            return default or type_()

    def ensure_cast[T](self, key: str, type_: type[T], default: T | None = None) -> T:
        """
        Get the value and try to cast it to the target type.

        Returns:
            value at path: if value found.
            default: if value not found.
            type(): if value not found and no default provided.

        """
        try:
            return type_(self._get_item(key))
        except:  # noqa: E722
            return default or type_()

    def expect[T](self, key: str, type_: type[T]) -> T:
        """
        Expect the value to be present and of the specified type.

        Returns:
            value at path.

        Raises:
            IndexError: if the index is out of range.
            TypeError: if the value is not of the expected type.
            TypeError: if chaining is enabled and the list is indexed with a string
            KeyError: if chaining is enabled and the key cannot be found.

        """
        val = self._get_item(key)
        if not isinstance(val, type_):
            raise TypeError(f"expected {val} to be {type_}, not {type(val)}")
        return val
