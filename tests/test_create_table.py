import unittest

from app.libs.functions import create_table


class TestCreateTableFunction(unittest.TestCase):

    def test_positive_case(self):
        entries = {"A": 1, "B": 2, "C": 3}
        title = "Test Table"
        expected_output = (
            "+---+---+\n| A | 1 |\n+---+---+\n| B | 2 |\n| C | 3 |\n+---+---+"
        )
        self.assertEqual(create_table(entries, title), expected_output)

    def test_negative_case(self):
        entries = {"X": 10, "Y": 20}
        title = "Negative Test"
        expected_output = "+---+----+\n| X | 10 |\n| Y | 20 |\n+---+----+\n"
        self.assertNotEqual(create_table(entries, title), expected_output)
