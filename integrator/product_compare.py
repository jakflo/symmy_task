from .product_validate import ProductSerializer
from .product_type import ProductTransformed, ProductType, ProductTransformedWithoutHash, ProductTransformedForPatch
from .models import Item
from typing import List, Dict
from rest_framework.exceptions import ValidationError
from .product_db_caches import ProductDbCachesInsert, ProductDbCachesUpdate
from utils.array_split_by_field import split_by_fields

""" necha erp data zvalidovat a upravit a porovna s DB - hleda chybejici a zmenene
pripravi data pro odeslani na API (props missing a differing) a po zavolani save_missing_to_db() a save_differing_to_db()
dane zmeny ulozi do DB """
class ProductCompare:
    def __init__(self, data: List[ProductType]):
        self.__db_items_for_insert: ProductDbCachesInsert = ProductDbCachesInsert()
        self.__db_items_for_update: ProductDbCachesUpdate = ProductDbCachesUpdate()
        self.__load(data)
        self.__compare()

    @property
    def missing(self) -> List[ProductTransformedWithoutHash]:
        return self.__missing

    @property
    def differing(self) -> List[ProductTransformedForPatch]:
        return self.__differing
    
    def save_missing_to_db(self):
        self.__db_items_for_insert.send_to_db()

    def save_differing_to_db(self):
        self.__db_items_for_update.send_to_db()

    def clear_missing_data(self):
        self.__missing = []

    def clear_differing_data(self):
        self.__differing = []

    """ API vratila, ze se odeslani nekterych polozek u nove vkladanych dat nepovedlo, tak se pripavime novy pokus:
    do DB vlozime polozky, kde se to povedlo a v self.__missing nechame, co je treba vlozit znova
    sku_list = pole s jejich id, kde se to nepovedlo """
    def prepare_resend_after_some_imports_failed_missing(self, sku_list: List[str]):
        split_items = split_by_fields(self.__missing, 'id', sku_list)
        ok_sku_list = [item['id'] for item in split_items['havent']]
        self.__db_items_for_insert.partial_send_to_db(ok_sku_list, True)
        self.__missing = split_items['have']

    # to same s polozkami editovanych dat
    def prepare_resend_after_some_imports_failed_differing(self, sku_list: List[str]):
        split_items = split_by_fields(self.__differing, 'id', sku_list)
        ok_sku_list = [item['id'] for item in split_items['havent']]
        self.__db_items_for_update.partial_send_to_db(ok_sku_list, True)
        self.__differing = split_items['have']
    
    def __compare(self):
        product_in_db = Item.objects.filter(source_id__in=self.__products.keys())
        product_in_db_map = {item.source_id: item for item in product_in_db}

        self.__missing: List[ProductTransformedWithoutHash] = []  # produkty, které v DB chybí
        self.__differing: List[ProductTransformedForPatch] = []  # produkty, které se liší (hash mismatch)
        db_fields = Item.get_data_fields()

        for sku, ext_item in self.__products.items():
            db_item = product_in_db_map.get(sku)
            if not db_item:
                # produkt není v DB
                ext_item_wo_hash = ext_item.copy()
                ext_item_wo_hash.pop("hash", None)
                self.__missing.append(self.__replace_source_id_with_id(ext_item_wo_hash))
                self.__db_items_for_insert.append(Item(**ext_item))

            elif db_item.hash != ext_item["hash"]:
                # hash se liší – připrav data pro PATCH
                patch_data = {'id': sku}
                for field in db_fields:
                    if getattr(db_item, field) != ext_item[field]:
                        setattr(db_item, field, ext_item[field])
                        patch_data[field] = ext_item[field]
                db_item.hash = ext_item["hash"]
                self.__differing.append(patch_data)
                self.__db_items_for_update.append(db_item)

    def __load(self, data: List[ProductType]):
        self.__products: Dict[str, ProductTransformed] = {}
        for product_raw in data:
            try:
                product = ProductSerializer(data=product_raw)
                product.is_valid(raise_exception=True)
                self.__products[product.data['source_id']] = product.data
            except ValidationError as e:
                print('validation error')
                print({'error': e.detail, 'data': product_raw})

    def __replace_source_id_with_id(self, input: Dict) -> Dict:
        output = {'id': input['source_id']}
        for key, item in input.items():
            if key != 'source_id':
                output[key] = item
        return output