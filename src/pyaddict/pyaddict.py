# -*- coding: utf-8 -*-
"""pyaddict"""
from __future__ import annotations
__copyright__ = ("Copyright (c) 2022 https://github.com/dxstiny")

import json
import re
from typing import Any, List, Optional, Tuple, Type, TypeVar, Union, overload

from pyaddict.types import JArray, JObject
from pyaddict.interfaces.common import ICommon, IExtended

T = TypeVar("T")

__all__ = ["JDict", "JList", "JListIterator"]


class JDict(JObject, IExtended):
    """dict extractor"""
    def __init__(self, data: Optional[JObject] = None) -> None:
        self._data = data or { }
        super().__init__(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def assertGet(self, key: str, type_: Type[T]) -> T:
        """
        asserts the key exists & is the specified type

        if the key does not exist, an exception is raised
        if the key exists but is not the specified type, an exception is raised

        raises AssertionError

        Usage: you know the key exists & is the specified type
        """
        assert key in self._data
        val = self._data[key]
        assert isinstance(val, type_)
        return val

    def optionalGet(self, key: str, type_: Type[T]) -> Optional[T]:
        """
        tries to get the key

        if the key does not exist, None is returned
        if the key exists but is not the specified type, None is returned

        Usage: you don't know if the key exists
        """
        try:
            value = self._data[key]
            if isinstance(value, type_):
                return value
            return None
        except: # pylint: disable=bare-except
            return None

    def optionalCast(self, key: str, type_: Type[T]) -> Optional[T]:
        """
        tries to get the key & cast to the specified type

        if the key does not exist, None is returned

        Usage: you don't know if the key exists & you don't care if it's the specified type
        """
        try:
            return type_(self._data[key]) # type: ignore
        except: # pylint: disable=bare-except
            return None

    def ensure(self, key: str, type_: Type[T], default: Optional[T] = None) -> T:
        """
        ensures the key exists & is the specified type

        if the key does not exist, the default value is returned
        if the key exists but is not the specified type, the default value is returned

        Usage: you don't know if the key exists, you care if it's the specified type
        but want a default value
        """
        try:
            value = self._data[key]
            if isinstance(value, type_):
                return value

            return default or type_()
        except: # pylint: disable=bare-except
            return default or type_()

    def ensureCast(self, key: str, type_: Type[T], default: Optional[T] = None) -> T:
        """
        ensures the key exists & is the specified type

        if the key does not exist, the default value is returned
        if the key exists but is not the specified type, the value is cast to the specified type

        Usage: you don't know if the key exists, you don't care if it's the specified type &
        you want a default value
        """
        try:
            return type_(self._data[key]) # type: ignore
        except: # pylint: disable=bare-except
            return default or type_()

    def toString(self, indent: Optional[int] = None) -> str:
        """returns the string representation of the data"""
        return json.dumps(self._data, indent=indent)

    def toDict(self) -> JObject:
        """returns the dict representation of the data"""
        return self._data

    @staticmethod
    def fromString(string: str) -> JDict:
        """returns a JDict from a string"""
        value = json.loads(string)
        if isinstance(value, dict):
            return JDict(value)
        return JDict()

    def chain(self) -> JChain:
        """
        equivalent to js optional chaining
        """
        return JChain(jdict = self)


class JList(JArray, IExtended):
    """list extractor"""
    def __init__(self, data: Optional[JArray] = None) -> None:
        self._data = data or [ ]
        super().__init__(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    @overload
    def get(self, index: int) -> Optional[Any]: ...
    @overload
    def get(self, index: int, default: Optional[T] = None) -> Union[Any, T]: ... # pylint: disable=arguments-differ

    def get(self, index: int, default: Optional[T] = None) -> Union[Any, T]: # pylint: disable=arguments-differ
        """
        returns the value at the specified index

        if the index does not exist, None is returned
        """
        if index < len(self._data):
            return self._data[index]
        return default

    def assertGet(self, index: int, type_: Type[T]) -> T: # pylint: disable=arguments-renamed
        """
        asserts the index exists & is the specified type

        if the index does not exist, an exception is raised
        if the index exists but is not the specified type, an exception is raised

        Usage: you know the index exists & is the specified type
        """
        assert index < len(self._data)
        val = self._data[index]
        assert isinstance(val, type_)
        return val

    def optionalGet(self, index: int, type_: Type[T]) -> Optional[T]: # pylint: disable=arguments-renamed
        """
        tries to get the index

        if the index does not exist, None is returned
        if the index exists but is not the specified type, None is returned

        Usage: you don't know if the index exists
        """
        try:
            value = self._data[index]
            if isinstance(value, type_):
                return value
            return None
        except: # pylint: disable=bare-except
            return None

    def optionalCast(self, index: int, type_: Type[T]) -> Optional[T]: # pylint: disable=arguments-renamed
        """
        tries to get the index & cast to the specified type

        if the index does not exist, None is returned

        Usage: you don't know if the index exists & you don't care if it's the specified type
        """
        try:
            return type_(self._data[index]) # type: ignore
        except: # pylint: disable=bare-except
            return None

    def ensure(self, index: int, type_: Type[T], default: Optional[T] = None) -> T: # pylint: disable=arguments-renamed
        """
        ensures the index exists & is the specified type

        if the index does not exist, the default value is returned
        if the index exists but is not the specified type, the default value is returned

        Usage: you don't know if the index exists, you care if it's the specified type
        but want a default value
        """
        try:
            value = self._data[index]
            if isinstance(value, type_):
                return value

            return default or type_()
        except: # pylint: disable=bare-except
            return default or type_()

    def ensureCast(self, index: int, type_: Type[T], default: Optional[T] = None) -> T: # pylint: disable=arguments-renamed
        """
        ensures the index exists & is the specified type

        if the index does not exist, the default value is returned
        if the index exists but is not the specified type, the value is cast to the specified type

        Usage: you don't know if the index exists, you don't care if it's the specified type &
        you want a default value
        """
        try:
            return type_(self._data[index]) # type: ignore
        except: # pylint: disable=bare-except
            return default or type_()

    def iterator(self) -> JListIterator:
        """
        returns an iterator selector for the list
        """
        return JListIterator(self)

    def toString(self, indent: Optional[int] = None) -> str:
        """returns the string representation of the data"""
        return json.dumps(self._data, indent=indent)

    def toList(self) -> JArray:
        """returns the list representation of the data"""
        return self._data

    @staticmethod
    def fromString(string: str) -> JList:
        """returns a JList from a string"""
        value = json.loads(string)
        if isinstance(value, list):
            return JList(value)
        return JList()

    def chain(self) -> JChain:
        """
        equivalent to js optional chaining
        """
        return JChain(jlist = self)


class JListIterator(JArray, ICommon):
    """list iterator"""
    def __init__(self, data: JList) -> None:
        self._data = data
        super().__init__(self._data)

    def assertGet(self, type_: Type[T]) -> List[T]: # pylint: disable=arguments-differ
        """
        iterates over the list & asserts each value is the specified type
        (which is usually the case for arrays)

        Usage: you know the values are the specified type
        """
        return [ self._data.assertGet(i, type_) for i, _ in enumerate(self._data) ]

    def optionalGet(self, type_: Type[T]) -> List[Optional[T]]: # pylint: disable=arguments-differ
        """
        iterates over the list & tries to get each with the specified type

        Usage: you don't know if the values are the specified type
        """
        return [ self._data.optionalGet(i, type_) for i, _ in enumerate(self._data) ]

    def optionalCast(self, type_: Type[T]) -> List[Optional[T]]: # pylint: disable=arguments-differ
        """
        iterates over the list & tries to cast each value to the specified type

        Usage: you don't know if the values are the specified type
        """
        return [ self._data.optionalGet(i, type_) for i, _ in enumerate(self._data) ]

    def ensure(self, type_: Type[T], default: Optional[T] = None) -> List[T]: # pylint: disable=arguments-differ
        """
        iterates over the list & ensures each value is the specified type

        Usage: you don't know if the values are the specified type & you want a default value
        """
        return [ self._data.ensure(i, type_, default) for i, _ in enumerate(self._data) ]

    def ensureCast(self, type_: Type[T], default: Optional[T] = None) -> List[T]: # pylint: disable=arguments-differ
        """
        iterates over the list & ensures each value is the specified type

        Usage: you don't know if the values are the specified type & you want a default value
        """
        return [ self._data.ensureCast(i, type_, default) for i, _ in enumerate(self._data) ]


class _ChainLink:
    """chain link"""
    def __init__(self, key: str) -> None:
        self._key: Union[str, int] = key
        self._optional = False
        self._index = False

        if key.endswith("?"):
            self._key = key[:-1]
            self._optional = True
        if key.startswith("[") and key.endswith("]"):
            self._key = int(key[1:-1])
            self._index = True

    def __repr__(self) -> str:
        return f"ChainLink({self._key}, optional={self._optional}, index={self._index})"

    @property
    def key(self) -> Union[str, int]:
        """returns the key"""
        return self._key

    @property
    def intKey(self) -> int:
        """returns the key as an int"""
        assert isinstance(self._key, int)
        return self._key

    @property
    def strKey(self) -> str:
        """returns the key as a string"""
        assert isinstance(self._key, str)
        return self._key

    @property
    def optional(self) -> bool:
        """returns true if the link is optional"""
        return self._optional

    @property
    def index(self) -> bool:
        """returns true if the link is an index"""
        return self._index


class JChain(ICommon):
    """optional chaining"""
    def __init__(self,
                 jdict: Optional[JDict] = None,
                 jlist: Optional[JList] = None) -> None:

        if jdict is None and jlist is None:
            raise Exception("JChain requires either a JDict or JList")

        self._jdict: Optional[JDict] = jdict
        self._jlist: Optional[JList] = jlist

    def _isDict(self) -> bool:
        return bool(self._jdict)

    def _isList(self) -> bool:
        return bool(self._jlist)

    def _createChainLinks(self, chain: str) -> List[_ChainLink]: # pylint: disable=no-self-use
        chain = re.sub(r"(\w)\[", r"\1.[", chain)
        return [ _ChainLink(key) for key in chain.split(".") ]

    def __getitem__(self, name: str) -> Any:
        value = self._prepare(name)
        if value is None:
            return None
        parent, key = value
        return parent.get(key)

    def _prepare(self,
                 chain: str,
                 preventException: bool = False) -> Optional[Tuple[IExtended, Union[str, int]]]:
        """
        prepares the chain for execution

        returns None if the chain is invalid
        else, returns (parent, last_key)
        """
        links = self._createChainLinks(chain)
        last = links.pop()
        nullable: Optional[Union[JObject, JArray]] = self._jdict if self._isDict() else self._jlist

        assert nullable is not None

        value = nullable

        for link in links:
            if preventException or link.optional:
                if link.index and link.intKey >= len(list(value)): # jlist
                    return None # couldn't resolve
                if not link.index and link.strKey not in value: # jdict
                    return None # couldn't resolve
            if isinstance(value, (JDict, dict)):
                value = value[link.strKey]
                continue
            assert isinstance(value, (JList, list))
            value = value[link.intKey]

        if last.index and isinstance(value, list):
            return JList(value), last.key
        if not last.index and isinstance(value, dict):
            return JDict(value), last.key
        return JDict(), last.key

    def resolve(self, chain: str) -> Any:
        """
        resolves the chain & returns the value

        raises an exception if the chain is invalid
        """
        value = self._prepare(chain)
        if value is None:
            raise KeyError(f"invalid chain: {chain}")
        parent, last = value
        assert isinstance(last, (int, str))
        return parent[last]

    def assertGet(self, chain: str, type_: Type[T]) -> T:
        """
        resolves the chain & returns the value

        raises an exception if the chain is invalid or the value is not the specified type
        """
        value = self._prepare(chain)
        if value is None:
            raise KeyError(f"invalid chain: {chain}")
        parent, last = value
        assert isinstance(last, (int, str))
        return parent.assertGet(last, type_)

    def optionalGet(self, chain: str, type_: Type[T]) -> Optional[T]: # pylint: disable=arguments-renamed
        """
        tries to resolve the chain

        if any key does not exist, None is returned
        if the chain resolves but is not the specified type, None is returned

        Usage: you don't know if the chain resolves
        """
        value = self._prepare(chain, preventException = True)
        if value is None:
            return None
        obj, last = value
        assert isinstance(last, (int, str))
        return obj.optionalGet(last, type_)

    def optionalCast(self, chain: str, type_: Type[T]) -> Optional[T]: # pylint: disable=arguments-renamed
        """
        tries to resolve the chain

        if any key does not exist, None is returned
        if the chain resolves but is not the specified type, None is returned

        Usage: you don't know if the chain resolves
        """
        value = self._prepare(chain, preventException = True)
        if value is None:
            return None
        obj, last = value
        assert isinstance(last, (int, str))
        return obj.optionalCast(last, type_)

    def ensure(self, chain: str, type_: Type[T], default: Optional[T] = None) -> T: # pylint: disable=arguments-renamed
        """
        tries to resolve the chain

        if any key does not exist, the default value is returned
        if the chain resolves but is not the specified type, the default value is returned

        Usage: you don't know if the chain resolves
        """
        value = self._prepare(chain, preventException = True)
        if value is None:
            return default or type_()
        obj, last = value
        assert isinstance(last, (int, str))
        return obj.ensure(last, type_, default)

    def ensureCast(self, chain: str, type_: Type[T], default: Optional[T] = None) -> T: # pylint: disable=arguments-renamed
        """
        tries to resolve the chain

        if any key does not exist, the default value is returned
        if the chain resolves but is not the specified type, the default value is returned

        Usage: you don't know if the chain resolves
        """
        value = self._prepare(chain, preventException = True)
        if value is None:
            return default or type_()
        obj, last = value
        assert isinstance(last, (int, str))
        return obj.ensureCast(last, type_, default)
