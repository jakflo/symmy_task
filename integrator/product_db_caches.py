from abc import ABC, abstractmethod
from .models import Item
from typing import List, Dict
from utils.array_split_by_field import split_by_fields

class ProductDbCachesBase(ABC):
    def __init__(self):
        self._items: List[Item] = []

    def append(self, item: Item):
        self._items.append(item)

    def send_to_db(self):
        self._send_to_db_items(self._items)

    def partial_send_to_db(self, sku_list: List[str], remove_sent_form_cache: bool):
        if len(sku_list) == 0:
            return
        
        split_items = split_by_fields(self._items, 'source_id', sku_list)
        if len(split_items) == 0:
            return
        
        self._send_to_db_items(split_items['have'])
        if (remove_sent_form_cache):
            self._items = split_items['havent']

    @abstractmethod
    def _send_to_db_items(self, items: List[Item]):
        pass


class ProductDbCachesInsert(ProductDbCachesBase):
    def _send_to_db_items(self, items: List[Item]):
        Item.objects.bulk_create(items, batch_size=1000)

class ProductDbCachesUpdate(ProductDbCachesBase):
    def _send_to_db_items(self, items: List[Item]):
        db_fields = Item.get_data_fields()
        db_fields.append("hash")
        Item.objects.bulk_update(items, db_fields, batch_size=1000)
