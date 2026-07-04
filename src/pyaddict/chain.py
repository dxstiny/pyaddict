import re
from typing import Any


class ChainLink:
    """chain link"""

    __slots__ = ("_key", "_optional", "_index", "_create_array")

    def __init__(self, key: str) -> None:
        self._key: str | int | None = key
        self._optional = False
        self._create_array = False
        self._index = False

        if key.endswith("?"):
            self._key = key[:-1]
            self._optional = True
        if key == "[]":
            self._key = None
            self._create_array = True
        elif key.startswith("[") and key.endswith("]"):
            self._key = int(key[1:-1])
            self._index = True

    def __repr__(self) -> str:
        return f"ChainLink({self._key}, optional={self._optional}, index={self._index})"

    @property
    def key(self) -> str | int | None:
        """returns the key"""
        return self._key

    @property
    def int_key(self) -> int:
        """returns the key as an int"""
        assert isinstance(self._key, int)
        return self._key

    @property
    def str_key(self) -> str:
        """returns the key as a string"""
        assert isinstance(self._key, str)
        return self._key

    @property
    def optional(self) -> bool:
        """returns true if the link is optional"""
        return self._optional

    @property
    def create_array(self) -> bool:
        """returns true if the link splits into an array"""
        return self._create_array

    @property
    def index(self) -> bool:
        """returns true if the link is an index"""
        return self._index

    @property
    def expect_object(self) -> bool:
        return not self.expect_list

    @property
    def expect_list(self) -> bool:
        return self.create_array or self.index

    @classmethod
    def create_chain(
        cls, chain: str, *, allow_first_int: bool = False
    ) -> list["ChainLink"]:
        if allow_first_int:
            chain = re.sub(r"^(\d+).", r"[\1].", chain)
            if re.match(r"^\d+$", chain):
                return [cls(f"[{chain}]")]

        chain = re.sub(r"(\w)\[", r"\1.[", chain)
        return [cls(key) for key in chain.split(".")]


def traverse(obj: Any, chain: list[ChainLink]) -> Any | None:
    if len(chain) == 0:
        return obj
    next_link, *next_chain = chain

    if next_link.optional and next_link.key and next_link.key not in obj:
        return None

    if next_link.create_array and isinstance(obj, list):
        return [traverse(x, next_chain) for x in obj]

    return traverse(obj[next_link.key], next_chain)
