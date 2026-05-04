from django.test import TestCase
from utils.array_split_by_field import split_by_field, split_by_fields


class Dummy:
    def __init__(self, name, color):
        self.name = name
        self.color = color

class SplitByFieldTest(TestCase):

    def test_split_with_single_value(self):
        data = [
            {"name": "a", "color": "red"},
            {"name": "b", "color": "blue"},
            {"name": "c", "color": "green"},
            {"name": "d", "color": "yellow"},
            Dummy("e", "red"),
            Dummy("f", "blue"),
            Dummy("g", "black"),
            {"name": "h"},  # missing field
        ]

        result = split_by_field(data, "color", "red")

        self.assertEqual(len(result["have"]), 2)
        self.assertEqual(len(result["havent"]), 6)

        # kontrola hodnot
        for item in result["have"]:
            if isinstance(item, dict):
                self.assertIn(item.get("color"), ["red"])
            else:
                self.assertIn(getattr(item, "color", None), ["red"])

    def test_split_with_multiple_values(self):
        data = [
            {"name": "a", "color": "red"},
            {"name": "b", "color": "blue"},
            {"name": "c", "color": "green"},
            {"name": "d", "color": "yellow"},
            Dummy("e", "red"),
            Dummy("f", "blue"),
            Dummy("g", "black"),
            {"name": "h"},  # missing field
        ]

        result = split_by_fields(data, "color", ["red", "blue", "green"])

        self.assertEqual(len(result["have"]), 5)
        self.assertEqual(len(result["havent"]), 3)

        # kontrola hodnot
        for item in result["have"]:
            if isinstance(item, dict):
                self.assertIn(item.get("color"), ["red", "blue", "green"])
            else:
                self.assertIn(getattr(item, "color", None), ["red", "blue", "green"])

    def test_empty_values(self):
        data = [
            {"color": "red"},
            Dummy("x", "red"),
        ]

        result = split_by_fields(data, "color", [])

        self.assertEqual(result["have"], [])
        self.assertEqual(len(result["havent"]), 2)

    def test_no_field(self):
        data = [
            {"name": "a"},
            Dummy("b", None),
        ]

        result = split_by_fields(data, "color", ["red"])

        self.assertEqual(result["have"], [])
        self.assertEqual(len(result["havent"]), 2)
