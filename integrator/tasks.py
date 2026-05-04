from celery import shared_task
from .product_type import ProductType
from typing import List
from .product_compare import ProductCompare
from .product_send_changes import ProductSendChanges
from .api_client import ApiRequestError

@shared_task
def process_erp_object(data: List[ProductType]):
    products = ProductCompare(data)
    product_send_changes = ProductSendChanges(products)
    try:
        product_send_changes.send_and_save()
    except ApiRequestError as e:
        print(f"Error sending product changes: {e}")
