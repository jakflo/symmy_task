from django.test import TestCase
from django.conf import settings
import responses
import json
from .product_compare import ProductCompare
from .product_send_changes import ProductSendChanges
from copy import deepcopy
from .models import Item
from typing import List

class TestDataSend(TestCase):
    @responses.activate
    def test_resend_missing(self):
        test_data = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price_vat_excl": 12400.5, "stocks": {"praha": 5, "brno": 3}, "attributes": {"color": "stříbrná"}},
            {"id": "SKU-003", "title": "Mlýnek", "price_vat_excl": 1500, "stocks": {"externi": 50}, "attributes": None},
            {"id": "SKU-006", "title": "Tablety", "price_vat_excl": 250, "stocks": {"praha": 100}, "attributes": {}},
            {"id": "SKU-008", "title": "Filtry", "price_vat_excl": 300, "stocks": {"praha": "N/A"}, "attributes": {"color": "bílá"}}
        ]
        expected_data_1 = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price": 15004.6, "stocks": 8, "color": "stříbrná"},
            {"id": "SKU-003", "title": "Mlýnek", "price": 1815, "stocks": 50, "color": "N/A"},
            {"id": "SKU-006", "title": "Tablety", "price": 302.5, "stocks": 100, "color": "N/A"},
            {"id": "SKU-008", "title": "Filtry", "price": 363, "stocks": 0, "color": "bílá"}
        ]
        expected_data_2 = [            
            {"id": "SKU-003", "title": "Mlýnek", "price": 1815, "stocks": 50, "color": "N/A"},
            {"id": "SKU-006", "title": "Tablety", "price": 302.5, "stocks": 100, "color": "N/A"}
        ]

        url = f"{settings.INTEGRATOR_API_BASE_URL}/products/"
        responses.add(responses.POST, url, json={
            'stat': 'some_imports_failed', 
            'failed_items_id': [
                'SKU-003', 
                'SKU-006', 
                'spatne_id'
            ]
        }, status=201)
        responses.add(responses.POST, url, json={'stat': 'ok'}, status=201)

        product_compare = ProductCompare(test_data)
        product_send_changes = ProductSendChanges(product_compare)
        product_send_changes.send_and_save()

        self.__check_request(responses.calls[0].request, 'POST', expected_data_1)
        self.__check_request(responses.calls[1].request, 'POST', expected_data_2)
        self.assertEqual(len(responses.calls), 2)
        self.__check_skus_in_db(['SKU-001', 'SKU-003', 'SKU-006', 'SKU-008'])

    @responses.activate
    def test_resend_differing(self):
        test_data_1 = [
            {"id": "SKU-001", "title": "Kávovar Espresso", "price_vat_excl": 12400.5, "stocks": {"praha": 5, "brno": 3}, "attributes": {"color": "stříbrná"}},
            {"id": "SKU-003", "title": "Mlýnek", "price_vat_excl": 1500, "stocks": {"externi": 50}, "attributes": None},
            {"id": "SKU-006", "title": "Tablety", "price_vat_excl": 250, "stocks": {"praha": 100}, "attributes": {}},
            {"id": "SKU-008", "title": "Filtry", "price_vat_excl": 300, "stocks": {"praha": "N/A"}, "attributes": {"color": "bílá"}}
        ]

        test_data_2 = deepcopy(test_data_1)
        test_data_2[0]['stocks'] = {"externi": 10}
        test_data_2[1]['stocks'] = {"externi": 11}
        test_data_2[2]['stocks'] = {"externi": 12}
        test_data_2[3]['stocks'] = {"externi": 13}

        expected_data_1 = [
            {"id": "SKU-001", "stocks": 10},
            {"id": "SKU-003", "stocks": 11},
            {"id": "SKU-006", "stocks": 12},
            {"id": "SKU-008", "stocks": 13}
        ]
        expected_data_2 = [            
            {"id": "SKU-003", "stocks": 11},
            {"id": "SKU-006", "stocks": 12}
        ]

        url = f"{settings.INTEGRATOR_API_BASE_URL}/products/"
        responses.add(responses.POST, url, json={'stat': 'ok'}, status=201)
        responses.add(responses.PATCH, url, json={
            'stat': 'some_imports_failed', 
            'failed_items_id': [
                'SKU-003', 
                'SKU-006', 
                'spatne_id'
            ]
        }, status=200)
        responses.add(responses.PATCH, url, json={'stat': 'ok'}, status=200)

        product_compare_1 = ProductCompare(test_data_1)
        product_send_changes_1 = ProductSendChanges(product_compare_1)
        product_send_changes_1.send_and_save()

        product_compare_2 = ProductCompare(test_data_2)
        product_send_changes_2 = ProductSendChanges(product_compare_2)
        product_send_changes_2.send_and_save()
        
        self.__check_request(responses.calls[1].request, 'PATCH', expected_data_1)
        self.__check_request(responses.calls[2].request, 'PATCH', expected_data_2)
        self.assertEqual(len(responses.calls), 3)
        self.__check_skus_in_db(['SKU-001', 'SKU-003', 'SKU-006', 'SKU-008'])


    def __check_request(self, api_request, expected_method: str, expected_data):        
        post_body = json.loads(api_request.body)
        headers = api_request.headers
        self.assertEqual(headers["X-Api-Key"], settings.INTEGRATOR_API_KEY)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(api_request.method, expected_method)        
        self.assertCountEqual(post_body, expected_data)

    def __check_skus_in_db(self, expected_sku_list: List[str]):
        records_count = Item.objects.all().count()
        self.assertEqual(records_count, len(expected_sku_list))

        records = Item.objects.filter(source_id__in=expected_sku_list)
        records_id = [item.source_id for item in records]
        self.assertCountEqual(records_id, expected_sku_list)

