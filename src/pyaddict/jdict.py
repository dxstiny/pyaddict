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

    def _get_item(self, key: str, *, optional: bool = False) -> Any | None:
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

    @overload
    def optional_get[V](
        self,
        key: str,
        type_: type[list],
        default: list[V] | None = None,
        *,
        value_type: type[V],
    ) -> list[V | None] | None: ...

    @overload
    def optional_get[K, V](
        self,
        key: str,
        type_: type[dict],
        default: dict[K, V] | None = None,
        *,
        key_type: type[K],
        value_type: type[V],
    ) -> dict[K, V | None] | None: ...

    def optional_get[T, K, V](
        self,
        key: str,
        type_: type[T] | None = None,
        default: T | None = None,
        *,
        key_type: type[K] | None = None,
        value_type: type[V] | None = None,
    ) -> Any | None:
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
        if value is None:
            return default

        if isinstance(value, list) and value_type is not None:
            return [x if isinstance(x, value_type) else None for x in value]

        if isinstance(value, dict) and value_type is not None and key_type is not None:
            return {
                k: v if isinstance(v, value_type) else None
                for k, v in value.items()
                if isinstance(k, key_type)
            }

        return value

    @overload
    def ensure[T](self, key: str, type_: type[T]): ...

    @overload
    def ensure[T](self, key: str, type_: type[T], default: T): ...

    @overload
    def ensure[V](
        self,
        key: str,
        type_: type[list],
        default: list[V] | None = None,
        *,
        value_type: type[V],
    ): ...

    @overload
    def ensure[K, V](
        self,
        key: str,
        type_: type[dict],
        default: dict[K, V] | None,
        *,
        key_type: type[K],
        value_type: type[V],
    ): ...

    def ensure[T, K, V](
        self,
        key: str,
        type_: type[T],
        default: T | None = None,
        *,
        key_type: type[K] | None = None,
        value_type: type[V] | None = None,
    ) -> Any:
        """
        Get the value if it matches the target type.

        Returns:
            value at path: if value found and has the expected type.
            default: if value not found or not the expected type.
            type(): if value not found and no default provided.

        """
        try:
            value = self._get_item(key)
            if isinstance(value, type_):
                if isinstance(value, list) and value_type is not None:
                    return [x for x in value if isinstance(x, value_type)]
                if (
                    isinstance(value, dict)
                    and value_type is not None
                    and key_type is not None
                ):
                    return {
                        k: v
                        for k, v in value.items()
                        if isinstance(k, key_type) and isinstance(v, value_type)
                    }

                return value
            return default or type_()
        except:  # noqa: E722
            return default or type_()

    @overload
    def ensure_cast[T](self, key: str, type_: type[T]): ...

    @overload
    def ensure_cast[T](self, key: str, type_: type[T], default: T): ...

    @overload
    def ensure_cast[V](
        self,
        key: str,
        type_: type[list],
        default: list[V] | None = None,
        *,
        value_type: type[V],
    ): ...

    @overload
    def ensure_cast[K, V](
        self,
        key: str,
        type_: type[dict],
        default: dict[K, V] | None,
        *,
        key_type: type[K],
        value_type: type[V],
    ): ...

    def ensure_cast[T, K, V](
        self,
        key: str,
        type_: type[T],
        default: T | None = None,
        *,
        key_type: type[K] | None = None,
        value_type: type[V] | None = None,
    ) -> T:
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

    @overload
    def expect[T](self, key: str, type_: type[T]) -> T: ...

    @overload
    def expect[V](
        self, key: str, type_: type[list], *, value_type: type[V]
    ) -> list[V]: ...

    @overload
    def expect[K, V](
        self, key: str, type_: type[dict], *, key_type: type[K], value_type: type[V]
    ) -> dict[K, V]: ...

    def expect[T, K, V](
        self,
        key: str,
        type_: type[T],
        *,
        key_type: type[K] | None = None,
        value_type: type[V] | None = None,
    ) -> T:
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
