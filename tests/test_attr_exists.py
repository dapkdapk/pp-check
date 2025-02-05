import unittest

from app.libs.ppinfo import AKPPInfo


class TestAttrExists(unittest.TestCase):

    def test_positive_case_exists(self):
        obj = {"a": {"b": {"c": 123}}}
        self.assertTrue(AKPPInfo.AttrExists(obj, int, "a", "b", "c"))

    def test_positive_case_exists_wrong_type(self):
        obj = {"a": {"b": {"c": "not an int"}}}
        self.assertFalse(AKPPInfo.AttrExists(obj, int, "a", "b", "c"))

    def test_positive_case_exists_no_type_check(self):
        obj = {"a": {"b": {"c": 123}}}
        self.assertTrue(AKPPInfo.AttrExists(obj, None, "a", "b", "c"))

    def test_negative_case_not_exists(self):
        obj = {"a": {"b": {"c": 123}}}
        self.assertFalse(AKPPInfo.AttrExists(obj, int, "a", "x", "c"))

    def test_negative_case_not_dict(self):
        obj = ["not", "a", "dict"]
        self.assertFalse(AKPPInfo.AttrExists(obj, int, "a"))

    def test_empty_dict(self):
        obj = {}
        self.assertFalse(AKPPInfo.AttrExists(obj, int, "a"))

    def test_empty_keys(self):
        obj = {"a": {"b": {"c": 123}}}
        self.assertFalse(AKPPInfo.AttrExists(obj, int))

    def test_nested_dict_with_multiple_levels(self):
        obj = {"a": {"b": {"c": {"d": 456}}}}
        self.assertTrue(AKPPInfo.AttrExists(obj, int, "a", "b", "c", "d"))

    def test_invalid_type_check(self):
        obj = {"a": {"b": {"c": 3.14}}}
        self.assertFalse(AKPPInfo.AttrExists(obj, int, "a", "b", "c"))

    def test_large_nested_structure(self):
        obj = {"a": {"b": {"c": {"d": {"e": {"f": {"g": 789}}}}}}}
        self.assertTrue(
            AKPPInfo.AttrExists(obj, int, "a", "b", "c", "d", "e", "f", "g")
        )

    def test_non_dict_structure(self):
        obj = None
        self.assertFalse(AKPPInfo.AttrExists(obj, int, "a"))
