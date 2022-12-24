# -*- coding: utf-8 -*-
"""pyaddict"""
__copyright__ = ("Copyright (c) 2022 https://github.com/dxstiny")

import unittest

from pyaddict import JDict
from pyaddict.pyaddict import JList, JListIterator
from pyaddict.schema import  Object, String, Integer, Float, Boolean, Array
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
        "dictlist": [
            {
                "stringvalue": "value3",
                "intvalue": 3,
                "floatvalue": 3.0,
                "boolvalue": True,
            },
            {
                "stringvalue": "value4",
                "intvalue": 4,
                "floatvalue": 4.0,
                "boolvalue": True,
            },
        ],
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

    def test_optionalCast(self) -> None:
        self.assertEqual(jdict.optionalCast("stringvalue", str), "value1")
        self.assertEqual(jdict.optionalCast("intvalue", int), 1)
        self.assertEqual(jdict.optionalCast("floatvalue", float), 1.0)
        self.assertEqual(jdict.optionalCast("boolvalue", bool), True)
        self.assertEqual(jdict.optionalCast("listvalue", list), [1, 2, 3])

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
    def test_usecase_dict(self) -> None:
        self.assertIsInstance(jdict.ensure("intAsString", int), int)
        self.assertEqual(jdict.ensure("intAsString", int), 0)

        self.assertIsInstance(jdict.ensureCast("intAsString", int), int)
        self.assertEqual(jdict.ensureCast("intAsString", int), 5)

        self.assertRaises(AssertionError, jdict.assertGet, "intAsString", int)

        self.assertEqual(jdict.optionalCast("intAsString", int), 5)

        self.assertIsNone(jdict.optionalGet("intAsString", int))

    def test_usecase_list(self) -> None:
        jlist = jdict.ensureCast("listvalue", JList)
        self.assertEqual(len(jlist), 3)

        self.assertEqual(jlist.assertGet(0, int), 1)
        self.assertEqual(jlist.assertGet(1, int), 2)
        self.assertEqual(jlist.assertGet(2, int), 3)
        self.assertRaises(AssertionError, jlist.assertGet, 3, int)

        self.assertEqual(jlist.optionalCast(0, int), 1)
        self.assertEqual(jlist.optionalCast(1, int), 2)
        self.assertEqual(jlist.optionalCast(2, int), 3)
        self.assertIsNone(jlist.optionalCast(3, int))

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
        self.assertEqual(jlist.iterator().optionalCast(int), [1, 2, 3])
        self.assertEqual(jlist.iterator().optionalCast(str), [None, None, None])
        self.assertEqual(jlist.iterator().optionalGet(int), [1, 2, 3])
        self.assertEqual(jlist.iterator().optionalGet(str), [None, None, None])

    def test_chaining(self) -> None:
        chain = jdict.chain()
        self.assertEqual(chain.ensureCast("dictvalue.listvalue", JList)
                              .iterator()
                              .ensure(int),
                         [2, 3, 4])
        self.assertEqual(chain.ensureCast("dictvalue.listvalue.[0]", int), 2)
        self.assertIsNone(chain.optionalGet("dictvalue.dictlist.[2]", dict))
        self.assertRaises(IndexError, chain.__getitem__, "dictvalue.dictlist.[2].value") # []
        self.assertIsNone(chain.optionalGet("dictvalue.dictlist.[2]?.stringvalue", str))

    def test_serialise(self) -> None:
        self.assertIsInstance(jdict.toString(), str)
        self.assertIsInstance(JDict.fromString(jdict.toString()), JDict)

        self.assertEqual(JList.fromString(jdict.toString()), [ ])

        self.assertIsInstance(JList.fromString(jdict.toString()), JList)
        self.assertIsInstance(JList.fromString(jdict.toString()).toString(), str)


class TestSchemas(unittest.TestCase):
    def test_schemas(self) -> None:
        schema = Object({
            "stringvalue": String(),
            "intvalue": Integer(),
            "floatvalue": Float(),
            "boolvalue": Boolean(),
            "listvalue": Array(Integer()),
            "intAsString": Integer().coerce(),
            "dictvalue": Object({
                "stringvalue": String(),
                "intvalue": Integer(),
                "floatvalue": Float(),
                "boolvalue": Boolean(),
                "listvalue": Array(Integer()),
                "dictlist": Array(Object({
                    "stringvalue": String(),
                    "intvalue": Integer(),
                    "floatvalue": Float(),
                    "boolvalue": Boolean(),
                }))
            })
        })
        self.assertIsInstance(schema(jdict)["intAsString"], int)
        self.assertEqual(schema.valid(jdict), True)
        self.assertEqual(schema.error(jdict), None)

    def test_schema_noadditional(self) -> None:
        schema = Object({
            "stringvalue": String()
        })
        self.assertEqual(schema.valid(jdict), False)

    def test_schema_int(self) -> None:
        schema = Integer().min(0, False).max(10, False)
        self.assertEqual(schema.valid(1.0), False)

        self.assertEqual(schema.valid(0), False)
        self.assertEqual(schema.valid(1), True)
        self.assertEqual(schema.valid(9), True)
        self.assertEqual(schema.valid(10), False)

        schema2 = Integer().min(0, True).max(10, False)
        self.assertEqual(schema2.valid(0), True)
        self.assertEqual(schema2.valid(1), True)
        self.assertEqual(schema2.valid(10), False)

if __name__ == '__main__':
    unittest.main()
