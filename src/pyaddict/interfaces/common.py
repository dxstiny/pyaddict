# -*- coding: utf-8 -*-
"""pyaddict"""
from __future__ import annotations
__copyright__ = ("Copyright (c) 2022 https://github.com/dxstiny")

from typing import Union, Optional, Any, Type, TypeVar, overload
from abc import ABC, abstractmethod


T = TypeVar("T")


class ICommon(ABC):
    """Common interface for all public class."""

    @abstractmethod
    def optionalCast(self, key: Union[str, int], type_: Type[T]) -> Optional[T]:
        """you want to handle non-existing keys, but don't care about deviating types"""

    @abstractmethod
    def optionalGet(self, key: Union[str, int], type_: Type[T]) -> Optional[T]:
        """you want to handle deviating data (extens dict.get() with a type)"""

    @abstractmethod
    def ensure(self, key: Union[str, int], type_: Type[T], default: Optional[T] = None) -> T:
        """you don't really know the data, but want to have a default value"""

    @abstractmethod
    def ensureCast(self, key: Union[str, int], type_: Type[T], default: Optional[T] = None) -> T:
        """
        you don't really know the data, don't care about the type
        but want to have a default value
        """


class IExtended(ICommon):
    """Extended interface for all public class."""

    @abstractmethod
    def assertGet(self, key: Union[str, int], type_: Type[T]) -> T:
        """you know the data"""

    @overload
    @abstractmethod
    def get(self, index: Union[str, int]) -> Optional[Any]: ...
    @overload
    @abstractmethod
    def get(self, index: Union[str, int], default: Optional[T] = None) -> Union[Any, T]: ...
    @abstractmethod
    def get(self, key: Union[str, int], default: Optional[T] = None) -> Union[T, Any]:
        """get exception safe value"""

    @abstractmethod
    def __getitem__(self, key: Union[str, int]) -> Any:
        """indexable"""
