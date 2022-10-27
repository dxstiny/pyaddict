# -*- coding: utf-8 -*-
"""pyaddict"""
__copyright__ = ("Copyright (c) 2022 https://github.com/dxstiny")

import unittest

from pyaddict import JDict
from pyaddict.pyaddict import JList, JListIterator
from pyaddict.types import JObject


dictionary: JObject = {
    "stringvalue": "value1",
    "intvalue": 1,
    "floatvalue": 1.0,
    "boolvalue": True,
    "listvalue": [1, 2, 3],
    "intAsString": "5",
    "dictvalue": {
        "stringvalue": "value2",
        "intvalue": 2,
        "floatvalue": 2.0,
        "boolvalue": True,
        "listvalue": [2, 3, 4],
    }
}

jdict = JDict(dictionary)


class TestAllDict(unittest.TestCase):
    def test_assertGet(self) -> None:
        self.assertEqual(jdict.assertGet("stringvalue", str), "value1")
        self.assertEqual(jdict.assertGet("intvalue", int), 1)
        self.assertEqual(jdict.assertGet("floatvalue", float), 1.0)
        self.assertEqual(jdict.assertGet("boolvalue", bool), True)
        self.assertEqual(jdict.assertGet("listvalue", list), [1, 2, 3])

    def test_tryGet(self) -> None:
        self.assertEqual(jdict.tryGet("stringvalue", str), "value1")
        self.assertEqual(jdict.tryGet("intvalue", int), 1)
        self.assertEqual(jdict.tryGet("floatvalue", float), 1.0)
        self.assertEqual(jdict.tryGet("boolvalue", bool), True)
        self.assertEqual(jdict.tryGet("listvalue", list), [1, 2, 3])

    def test_ensure(self) -> None:
        self.assertEqual(jdict.ensure("stringvalue", str), "value1")
        self.assertEqual(jdict.ensure("intvalue", int), 1)
        self.assertEqual(jdict.ensure("floatvalue", float), 1.0)
        self.assertEqual(jdict.ensure("boolvalue", bool), True)
        self.assertEqual(jdict.ensure("listvalue", list), [1, 2, 3])

    def test_ensureCast(self) -> None:
        self.assertEqual(jdict.ensureCast("stringvalue", str), "value1")
        self.assertEqual(jdict.ensureCast("intvalue", int), 1)
        self.assertEqual(jdict.ensureCast("floatvalue", float), 1.0)
        self.assertEqual(jdict.ensureCast("boolvalue", bool), True)
        self.assertEqual(jdict.ensureCast("listvalue", list), [1, 2, 3])

    def test_nested(self) -> None:
        self.assertEqual(jdict.ensureCast("dictvalue", JDict)
                                    .assertGet("stringvalue", str),
                         "value2")
        self.assertEqual(jdict.ensureCast("dictvalue", JDict)
                                    .assertGet("intvalue", int),
                         2)
        self.assertEqual(jdict.ensureCast("dictvalue", JDict)
                                    .assertGet("floatvalue", float),
                         2.0)
        self.assertEqual(jdict.ensureCast("dictvalue", JDict)
                                    .assertGet("boolvalue", bool),
                         True)
        self.assertEqual(jdict.ensureCast("dictvalue", JDict)
                                    .assertGet("listvalue", list),
                         [2, 3, 4])


class TestUseCases(unittest.TestCase):
    def test_usecase1(self) -> None:
        self.assertIsInstance(jdict.ensure("intAsString", int), int)
        self.assertEqual(jdict.ensure("intAsString", int), 0)

        self.assertIsInstance(jdict.ensureCast("intAsString", int), int)
        self.assertEqual(jdict.ensureCast("intAsString", int), 5)

        self.assertRaises(AssertionError, jdict.assertGet, "intAsString", int)

        self.assertEqual(jdict.tryGet("intAsString", int), 5)

        self.assertIsNone(jdict.optionalGet("intAsString", int))

    def test_usecase2(self) -> None:
        jlist = jdict.ensureCast("listvalue", JList)
        self.assertEqual(len(jlist), 3)

        self.assertEqual(jlist.assertGet(0, int), 1)
        self.assertEqual(jlist.assertGet(1, int), 2)
        self.assertEqual(jlist.assertGet(2, int), 3)
        self.assertRaises(AssertionError, jlist.assertGet, 3, int)

        self.assertEqual(jlist.tryGet(0, int), 1)
        self.assertEqual(jlist.tryGet(1, int), 2)
        self.assertEqual(jlist.tryGet(2, int), 3)
        self.assertIsNone(jlist.tryGet(3, int))

        self.assertEqual(jlist.ensure(0, int), 1)
        self.assertEqual(jlist.ensure(1, int), 2)
        self.assertEqual(jlist.ensure(2, int), 3)
        self.assertEqual(jlist.ensure(3, int), 0)

        self.assertEqual(jlist.ensureCast(0, str), "1")
        self.assertEqual(jlist.ensureCast(1, str), "2")
        self.assertEqual(jlist.ensureCast(2, str), "3")
        self.assertEqual(jlist.ensureCast(3, str), "")

        self.assertIsInstance(jlist.iterator(), JListIterator)
        self.assertEqual(list(jlist.iterator()), [1, 2, 3])

        self.assertEqual(jlist.iterator().ensure(int), [1, 2, 3])
        self.assertEqual(jlist.iterator().ensure(str), ["", "", ""])
        self.assertEqual(jlist.iterator().ensureCast(int), [1, 2, 3])
        self.assertEqual(jlist.iterator().ensureCast(str), ["1", "2", "3"])
        self.assertEqual(jlist.iterator().assertGet(int), [1, 2, 3])
        self.assertRaises(AssertionError, jlist.iterator().assertGet, str)
        self.assertEqual(jlist.iterator().tryGet(int), [1, 2, 3])
        self.assertEqual(jlist.iterator().tryGet(str), [None, None, None])
        self.assertEqual(jlist.iterator().optionalGet(int), [1, 2, 3])
        self.assertEqual(jlist.iterator().optionalGet(str), [None, None, None])

    def test_serialise(self) -> None:
        self.assertIsInstance(jdict.toString(), str)
        self.assertIsInstance(JDict.fromString(jdict.toString()), JDict)

        self.assertEqual(JList.fromString(jdict.toString()), [ ])

        self.assertIsInstance(JList.fromString(jdict.toString()), JList)
        self.assertIsInstance(JList.fromString(jdict.toString()).toString(), str)

if __name__ == '__main__':
    unittest.main()
