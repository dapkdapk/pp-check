import unittest

from app.ppcheck import _short


class TestShortFunction(unittest.TestCase):

    # Positive Test Cases
    def test_shortening_long_string(self):
        self.assertEqual(_short("Hello, this is a long string.", 10), "Hello, thi...")

    def test_exact_length_string(self):
        self.assertEqual(_short("Hello", 5), "Hello")

    def test_short_string(self):
        self.assertEqual(_short("Hi", 10), "Hi")

    def test_custom_ends(self):
        self.assertEqual(
            _short("Hello, this is a long string.", 10, "!!"), "Hello, thi!!"
        )

    # Negative Test Cases
    def test_empty_string(self):
        self.assertEqual(_short("", 10), "")

    def test_non_string_input(self):
        with self.assertRaises(TypeError):
            _short(12345, 10)

    # Boundary Test Cases
    def test_boundary_case_just_over_length(self):
        self.assertEqual(_short("Hello, world!", 12), "Hello, world...")

    def test_boundary_case_exact_length(self):
        self.assertEqual(_short("Hello, world!", 13), "Hello, world!")

    def test_boundary_case_just_under_length(self):
        self.assertEqual(_short("Hello, world!", 14), "Hello, world!")
