# -*- coding: utf-8 -*-
"""pyaddict"""
from __future__ import annotations
__copyright__ = ("Copyright (c) 2022 https://github.com/dxstiny")

import json
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

from pyaddict.types import JArray, JObject

T = TypeVar("T")

__all__ = ["JDict", "JList", "JListIterator"]


class JDict(JObject):
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

    def tryGet(self, key: str, type_: Type[T]) -> Optional[T]:
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


class JList(JArray):
    """list extractor"""
    def __init__(self, data: Optional[JArray] = None) -> None:
        self._data = data or [ ]
        super().__init__(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def assertGet(self, index: int, type_: Type[T]) -> T:
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

    def optionalGet(self, index: int, type_: Type[T]) -> Optional[T]:
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

    def tryGet(self, index: int, type_: Type[T]) -> Optional[T]:
        """
        tries to get the index & cast to the specified type

        if the index does not exist, None is returned

        Usage: you don't know if the index exists & you don't care if it's the specified type
        """
        try:
            return type_(self._data[index]) # type: ignore
        except: # pylint: disable=bare-except
            return None

    def ensure(self, index: int, type_: Type[T], default: Optional[T] = None) -> T:
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

    def ensureCast(self, index: int, type_: Type[T], default: Optional[T] = None) -> T:
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


class JListIterator(JArray):
    """list iterator"""
    def __init__(self, data: JList) -> None:
        self._data = data
        super().__init__(self._data)

    def assertGet(self, type_: Type[T]) -> List[T]:
        """
        iterates over the list & asserts each value is the specified type
        (which is usually the case for arrays)

        Usage: you know the values are the specified type
        """
        return [ self._data.assertGet(i, type_) for i, _ in enumerate(self._data) ]

    def optionalGet(self, type_: Type[T]) -> List[Optional[T]]:
        """
        iterates over the list & tries to get each with the specified type

        Usage: you don't know if the values are the specified type
        """
        return [ self._data.optionalGet(i, type_) for i, _ in enumerate(self._data) ]

    def tryGet(self, type_: Type[T]) -> List[Optional[T]]:
        """
        iterates over the list & tries to cast each value to the specified type

        Usage: you don't know if the values are the specified type
        """
        return [ self._data.optionalGet(i, type_) for i, _ in enumerate(self._data) ]

    def ensure(self, type_: Type[T], default: Optional[T] = None) -> List[T]:
        """
        iterates over the list & ensures each value is the specified type

        Usage: you don't know if the values are the specified type & you want a default value
        """
        return [ self._data.ensure(i, type_, default) for i, _ in enumerate(self._data) ]

    def ensureCast(self, type_: Type[T], default: Optional[T] = None) -> List[T]:
        """
        iterates over the list & ensures each value is the specified type

        Usage: you don't know if the values are the specified type & you want a default value
        """
        return [ self._data.ensureCast(i, type_, default) for i, _ in enumerate(self._data) ]


class JChain:
    """optional chaining"""
    def __init__(self,
                 jdict: Optional[JDict] = None,
                 jlist: Optional[JList] = None) -> None:

        if jdict is None and jlist is None:
            raise Exception("JChain requires either a JDict or JList")

        if jdict is not None:
            self._jdict = jdict
            self._jlist = None

        if jlist is not None:
            self._jdict = None
            self._jlist = jlist

    class ChainLink:
        def __init__(self, key: str) -> None:
            self._key = key
            self._optional = False
            self._index = False

            if key.endswith("?"):
                key = key[:-1]
                self._optional = True
            if key.startswith("[") and key.endswith("]"):
                key = int(key[1:-1])
                self._index = True

            self._key = key

        def __repr__(self) -> str:
            return f"ChainLink({self._key}, optional={self._optional}, index={self._index})"

        def isOptional(self) -> bool:
            return False

        @property
        def key(self) -> str:
            return self._key

        @property
        def optional(self) -> bool:
            return self._optional

        @property
        def index(self) -> bool:
            return self._index

    def _isDict(self) -> bool:
        return bool(self._jdict)

    def _isList(self) -> bool:
        return bool(self._jlist)

    def _createChainLink(self, chain: str) -> List[JChain.ChainLink]:
        return [ JChain.ChainLink(key) for key in chain.split(".") ]

    def _prepare(self, chain: str) -> Optional[Tuple[Union[JDict, JList], str]]:
        chain = self._createChainLink(chain)
        last = chain.pop()
        value = self._jdict if self._isDict() else self._jlist
        for link in chain:
            if link.optional:
                if link.index and link.key >= len(list(value)):
                    return None
                if not link.index and link.key not in value:
                    return None
            value = value[link.key]
        return (JList(value) if last.index else JDict(value), last.key)

    def assertGet(self, chain: str, type_: Type[T]) -> Optional[T]:
        """
        asserts the chain resolves & is the specified type

        if any key does not exist, an exception is raised
        if the chain resolves but is not the specified type, an exception is raised

        raises AssertionError

        Usage: you know the chain resolves & is the specified type
        """
        value = self._prepare(chain)
        assert value is not None
        obj, last = value
        returnValue = obj.assertGet(last, type_)
        return returnValue

    def optionalGet(self, chain: str, type_: Type[T]) -> Optional[T]:
        """
        tries to resolve the chain

        if any key does not exist, None is returned
        if the chain resolves but is not the specified type, None is returned

        Usage: you don't know if the chain resolves
        """
        value = self._prepare(chain)
        if value is None:
            return None
        obj, last = value
        returnValue = obj.optionalGet(last, type_)
        return returnValue

    def tryGet(self, chain: str, type_: Type[T]) -> Optional[T]:
        """
        tries to resolve the chain

        if any key does not exist, None is returned
        if the chain resolves but is not the specified type, None is returned

        Usage: you don't know if the chain resolves
        """
        value = self._prepare(chain)
        if value is None:
            return None
        obj, last = value
        returnValue = obj.tryGet(last, type_)
        return returnValue

    def ensure(self, chain: str, type_: Type[T], default: Optional[T] = None) -> T:
        """
        tries to resolve the chain

        if any key does not exist, the default value is returned
        if the chain resolves but is not the specified type, the default value is returned

        Usage: you don't know if the chain resolves
        """
        value = self._prepare(chain)
        if value is None:
            return default
        obj, last = value
        returnValue = obj.ensure(last, type_, default)
        return returnValue

    def ensureCast(self, chain: str, type_: Type[T], default: Optional[T] = None) -> T:
        """
        tries to resolve the chain

        if any key does not exist, the default value is returned
        if the chain resolves but is not the specified type, the default value is returned

        Usage: you don't know if the chain resolves
        """
        value = self._prepare(chain)
        if value is None:
            return default
        obj, last = value
        returnValue = obj.ensureCast(last, type_, default)
        return returnValue
