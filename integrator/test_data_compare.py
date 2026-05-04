from django.test import TestCase
from .product_compare import ProductCompare

class TestDataCompare(TestCase):
    def test_new_product(self):
        test_data = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price_vat_excl": 12400.5, "stocks": {"praha": 5, "brno": 3}, "attributes": {"color": "stříbrná"}},
            {"id": "SKU-006", "title": "Tablety", "price_vat_excl": 250, "stocks": {"praha": 100}, "attributes": {}}
        ]
        expected_data = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price": 15004.6, "stocks": 8, "color": "stříbrná"},
            {"id": "SKU-006", "title": "Tablety", "price": 302.5, "stocks": 100, "color": "N/A"}
        ]
        product_compare = ProductCompare(test_data)
        self.assertCountEqual(product_compare.missing, expected_data)
        self.assertCountEqual(product_compare.differing, [])
        product_compare.save_missing_to_db()

        test_data.append({"id": "SKU-008", "title": "Filtry", "price_vat_excl": 300, "stocks": {"praha": "N/A"}, "attributes": {"color": "bílá"}})
        expected_data = [
            {"id": "SKU-008", "title": "Filtry", "price": 363, "stocks": 0, "color": "bílá"}
        ]
        product_compare = ProductCompare(test_data)
        self.assertCountEqual(product_compare.missing, expected_data)
        product_compare.save_missing_to_db()

        product_compare = ProductCompare(test_data)
        self.assertCountEqual(product_compare.missing, [])

    # je-li v datech vice polozek se stejnym id, plati ta posledni
    def test_duplicate_product(self):
        test_data = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price_vat_excl": 12400.5, "stocks": {"praha": 5, "brno": 3}, "attributes": {"color": "stříbrná"}},
            {"id": "SKU-006", "title": "Tablety", "price_vat_excl": 250, "stocks": {"praha": 100}, "attributes": {}},
            {"id": "SKU-001", "title": "Kávovar Espresso", "price_vat_excl": 13000, "stocks": {"praha": 10, "brno": 3}, "attributes": {"color": "stříbrná"}}
        ]
        expected_data = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price": 15730, "stocks": 13, "color": "stříbrná"},
            {"id": "SKU-006", "title": "Tablety", "price": 302.5, "stocks": 100, "color": "N/A"}
        ]
        product_compare = ProductCompare(test_data)
        self.assertCountEqual(product_compare.missing, expected_data)        

    def test_differing_product(self):
        test_data = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price_vat_excl": 12400.5, "stocks": {"praha": 5, "brno": 3}, "attributes": {"color": "stříbrná"}},
            {"id": "SKU-006", "title": "Tablety", "price_vat_excl": 250, "stocks": {"praha": 100}, "attributes": {}}
        ]
        product_compare = ProductCompare(test_data)
        product_compare.save_missing_to_db()

        test_data[0]["price_vat_excl"] = 13000
        test_data[0]["stocks"]["praha"] = 10
        expected_data = [
            {"id": "SKU-001", "price": 15730.0, "stocks": 13}
        ]
        product_compare = ProductCompare(test_data)
        self.assertCountEqual(product_compare.differing, expected_data)
        self.assertCountEqual(product_compare.missing, [])
        product_compare.save_differing_to_db()

        product_compare = ProductCompare(test_data)
        self.assertCountEqual(product_compare.differing, [])