# -*- coding: utf-8 -*-
"""pyaddict"""
from __future__ import annotations
__copyright__ = ("Copyright (c) 2022 https://github.com/dxstiny")

import json
from typing import Any, Dict, List, Optional, Type, TypeVar

from pyaddict.types import JArray, JObject

T = TypeVar("T")

__all__ = ["JDict", "JList", "JListIterator"]


class JDict(JObject):
    """dict extractor"""
    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
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
        tries to get the key & cast to the specified type

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


class JList(JArray):
    """list extractor"""
    def __init__(self, data: Optional[List[Any]] = None) -> None:
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
        tries to get the index & cast to the specified type

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
        iterates over the list & tries to cast each value to the specified type

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
