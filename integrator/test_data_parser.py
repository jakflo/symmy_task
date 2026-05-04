from django.test import TestCase
from .product_validate import ProductSerializer
from rest_framework.exceptions import ValidationError

class TestDataParser(TestCase):
    def test_basic_parse(self):
        test_data = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price_vat_excl": 12400.5, "stocks": {"praha": 5, "brno": 3}, "attributes": {"color": "stříbrná"}},
            {"id": "SKU-006", "title": "Tablety", "price_vat_excl": 250, "stocks": {"praha": 100}, "attributes": {}},
            {"id": "SKU-008", "title": "Filtry", "price_vat_excl": 300, "stocks": {"praha": "N/A"}, "attributes": {"color": "bílá"}}
        ]
        expected_data = [
            {"source_id": "SKU-001", "title": "Kávovar Espresso", "price": 15004.6, "stocks": 8, "color": "stříbrná", "hash": "c98c382cf656082a94fe5e72248c610d"},
            {"source_id": "SKU-006", "title": "Tablety", "price": 302.5, "stocks": 100, "color": "N/A", "hash": "0cf04bbf60b7c0eaf89ad336978688de"},
            {"source_id": "SKU-008", "title": "Filtry", "price": 363, "stocks": 0, "color": "bílá", "hash": "788a2ad6fcd47d02d9f9d8770ca2738c"}
        ]

        for k in range(len(test_data)):
            product = ProductSerializer(data=test_data[k])
            product.is_valid(raise_exception=True)
            self.assertDictEqual(product.data, expected_data[k])

    def test_invalid_data(self):
        log_text = 'looooooooooooooonooooooooooooonooooooooooooonooooooooooooonooooooooooooonooooooooooooonoooooooooooooong'

        invalid_data = [
            {"id": "SKU-004", "title": "Hrnek", "price_vat_excl": None, "stocks": {"praha": 10}, "attributes": {"color": "černá"}},
            {"id": "SKU-002", "title": "Neplatný produkt", "price_vat_excl": 100, "stocks": {"praha": "invalid"}, "attributes": {}},
            {"id": "SKU-002", "title": None, "price_vat_excl": 100, "stocks": {"praha": 10}, "attributes": {"color": "černá"}},
            {"id": None, "title": "Hrnek", "price_vat_excl": 100, "stocks": {"praha": 10}, "attributes": {"color": "černá"}},
            {"id": "SKU-002", "title": "Sleva - chyba", "price_vat_excl": -150.0, "stocks": {"praha": 10}, "attributes": {}},
            {"id": "SKU-002", "title": "qq", "price_vat_excl": 20, "stocks": {"praha": 10}, "attributes": {}},
            {"id": "SKU-002", "title": log_text, "price_vat_excl": 20, "stocks": {"praha": 10}, "attributes": {}},
        ]

        for k in range(len(invalid_data)):
            with self.assertRaises(ValidationError):
                product = ProductSerializer(data=invalid_data[k])
                product.is_valid(raise_exception=True)
