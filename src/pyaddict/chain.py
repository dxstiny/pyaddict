"""Chaining definition and helpers."""

import re
from typing import Any


class ChainLink:

    """chain link."""

    __slots__ = ("_key", "_optional", "_index", "_create_array")

    def __init__(
        self, key: str | int | None, optional: bool = False, create_array: bool = False
    ) -> None:
        """Create new chain link object."""
        self._key: str | int | None = key
        self._optional = optional
        self._create_array = create_array
        self._index = isinstance(key, int)

    def __repr__(self) -> str:
        """
        Return string representation.

        Returns:
            String representation.

        """
        return f"ChainLink({self._key}, optional={self._optional}, index={
            self._index
        }, create_array={self._create_array})"

    @property
    def key(self) -> str | int | None:
        """Key."""
        return self._key

    @property
    def int_key(self) -> int:
        """Key as an int."""
        if not isinstance(self._key, int):
            return -1
        return self._key

    @property
    def str_key(self) -> str:
        """Key as a string."""
        if not isinstance(self._key, str):
            return ""
        return self._key

    @property
    def optional(self) -> bool:
        """True if the link is optional."""
        return self._optional

    @optional.setter
    def optional(self, v: bool) -> None:
        self._optional = v

    @property
    def create_array(self) -> bool:
        """True if the link splits into an array."""
        return self._create_array

    @property
    def index(self) -> bool:
        """True if the link is an index."""
        return self._index

    @property
    def expect_object(self) -> bool:
        """Whether the link can be used on a dict."""
        return not self.expect_list

    @property
    def expect_list(self) -> bool:
        """Whether the link can be used on a list."""
        return self.create_array or self.index

    @property
    def stringify(self) -> str:
        """The friendly path."""
        out: str = self.str_key
        if self._create_array:
            out = "[]"
        elif self._index:
            out = f"[{self._key}]"
        if self._optional:
            out += "?"
        return out

    @classmethod
    def create(cls, key: str, *, optional: bool = False) -> "ChainLink":
        """
        Parse and create a single chain link.

        Args:
            key: link key to parse
            optional: force optional

        Returns:
            chain link

        """
        if key.endswith("?"):
            key = key[:-1]
            optional = True
        if key == "[]":
            return cls(key, optional, create_array=True)
        if key.startswith("[") and key.endswith("]"):
            return cls(int(key[1:-1]), optional)
        return cls(key, optional)

    @classmethod
    def create_chain(
        cls, chain: str, *, allow_first_int: bool = False, last_optional: bool = False
    ) -> list["ChainLink"]:
        """
        Parse and return a chain.

        Returns:
            full chain.

        """
        if allow_first_int:
            chain = re.sub(r"^(\d+).", r"[\1].", chain)
            if re.match(r"^\d+$", chain):
                return [cls.create(f"[{chain}]", optional=last_optional)]

        chain = re.sub(r"(\w)\[", r"\1.[", chain)

        links = [cls.create(key) for key in chain.split(".")]
        links[-1].optional = last_optional
        return links

    @staticmethod
    def path(stack: list["ChainLink"]) -> str:
        """
        Return the friendly path.

        Returns:
            friendly path.

        """
        return ".".join([x.stringify for x in stack])


def traverse(
    obj: Any, chain: list[ChainLink], *, stack: list[ChainLink] | None = None
) -> Any | None:
    """
    Resolve the chain recursively.

    Returns:
        obj: if chain end found.
        None: if link optional and not found.

    Raises:
        IndexError: if a non-optional index is out of range
        KeyError: if a non-optional key is not found

    """
    if len(chain) == 0 or obj is None:
        return obj

    if stack is None:
        stack = []

    next_link, *next_chain = chain
    stack.append(next_link)

    if next_link.optional and next_link.key is not None:
        if isinstance(obj, list) and (
            next_link.int_key < 0 or next_link.int_key >= len(obj)
        ):
            return None
        if isinstance(obj, dict) and next_link.key not in obj:
            return None

    if next_link.create_array and isinstance(obj, list):
        return [traverse(x, next_chain, stack=stack) for x in obj]

    try:
        next_item = obj[next_link.key]
    except IndexError as e:
        raise IndexError(
            f"list index {next_link.int_key} out of range (path={
                ChainLink.path(stack)
            })"
        ) from e
    except KeyError as e:
        raise KeyError(
            f"key {next_link.str_key} not found (path={ChainLink.path(stack)})"
        ) from e
    return traverse(next_item, next_chain, stack=stack)
