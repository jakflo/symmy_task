from django.test import TestCase
from django.conf import settings
import responses
import json
from .product_compare import ProductCompare
from .product_send_changes import ProductSendChanges
from unittest.mock import patch
from copy import deepcopy

class TestDataSend(TestCase):
    @responses.activate
    def test_send_and_save(self):
        test_data_1 = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price_vat_excl": 12400.5, "stocks": {"praha": 5, "brno": 3}, "attributes": {"color": "stříbrná"}},
            {"id": "SKU-003", "title": "Mlýnek", "price_vat_excl": 1500, "stocks": {"externi": 50}, "attributes": None}
        ]
        product_compare = ProductCompare(test_data_1)
        product_compare.save_missing_to_db()

        test_data_2 = deepcopy(test_data_1)
        test_data_2[0]['title'] = 'Kávovar Espresso 2'
        test_data_2[0]['attributes']['color'] = 'žlutá'
        test_data_2[1]['price_vat_excl'] = 1200
        test_data_2.extend([
            {"id": "SKU-006", "title": "Tablety", "price_vat_excl": 250, "stocks": {"praha": 100}, "attributes": {}},
            {"id": "SKU-008", "title": "Filtry", "price_vat_excl": 300, "stocks": {"praha": "N/A"}, "attributes": {"color": "bílá"}}
        ])

        excepted_post_data = [
            {"id": "SKU-006", "title": "Tablety", "price": 302.5, "stocks": 100, "color": "N/A"},
            {"id": "SKU-008", "title": "Filtry", "price": 363, "stocks": 0, "color": "bílá"}
        ]
        excepted_patch_data = [
            {"id": "SKU-001", "title": "Kávovar Espresso 2", "color": "žlutá"},
            {"id": "SKU-003", "price": 1452}
        ]

        url = f"{settings.INTEGRATOR_API_BASE_URL}/products/"
        product_compare = ProductCompare(test_data_2)
        product_send_changes = ProductSendChanges(product_compare)

        responses.add(responses.POST, url, json={'stat': 'ok'}, status=201)
        responses.add(responses.PATCH, url, json={'stat': 'ok'}, status=200)
        product_send_changes.send_and_save()

        post_request = responses.calls[0].request
        headers = post_request.headers
        post_body = json.loads(post_request.body)
        self.assertEqual(post_request.method, "POST")
        self.assertEqual(headers["X-Api-Key"], settings.INTEGRATOR_API_KEY)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertCountEqual(post_body, excepted_post_data)

        patch_request = responses.calls[1].request
        headers = patch_request.headers
        patch_body = json.loads(patch_request.body)
        self.assertEqual(patch_request.method, "PATCH")
        self.assertEqual(headers["X-Api-Key"], settings.INTEGRATOR_API_KEY)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertCountEqual(patch_body, excepted_patch_data)

    # poradi si, kdyz server vrati 429?
    @responses.activate
    @patch("integrator.api_client.time.sleep", return_value=None)
    def test_retry_after_429(self, mocked_sleep):
        test_data = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price_vat_excl": 12400.5, "stocks": {"praha": 5, "brno": 3}, "attributes": {"color": "stříbrná"}},
            {"id": "SKU-003", "title": "Mlýnek", "price_vat_excl": 1500, "stocks": {"externi": 50}, "attributes": None}
        ]

        url = f"{settings.INTEGRATOR_API_BASE_URL}/products/"

        # 1. pokus → 429
        responses.add(responses.POST, url, status=429)
        # 2. pokus → OK
        responses.add(responses.POST, url, json={'stat': 'ok'}, status=201)

        product_compare = ProductCompare(test_data)
        product_send_changes = ProductSendChanges(product_compare)
        product_send_changes.send_and_save()
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].response.json(), {'stat': 'ok'})
        mocked_sleep.assert_called_once_with(2)
        