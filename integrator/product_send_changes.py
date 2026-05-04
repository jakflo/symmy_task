from .product_compare import ProductCompare
from .api_client import send_api_request
from django.conf import settings
from utils.exceptions import ApiRequestError

#posle nalezene zmeny do API, pokud se povede, tak zmeny ulozi do DB
class ProductSendChanges():
    def __init__(self, changed_products: ProductCompare):
        self.__changed_products = changed_products

    def send_and_save(self):
        for x in range(0, 10):
            if len(self.__changed_products.missing) > 0:
                resp = self.__send_to_api("post", "/products/", self.__changed_products.missing)
                if resp['stat'] == 'ok':
                    self.__changed_products.save_missing_to_db()
                    self.__changed_products.clear_missing_data()
                elif resp['stat'] == 'some_imports_failed':
                    self.__changed_products.prepare_resend_after_some_imports_failed_missing(resp['failed_items_id'])
            
            if len(self.__changed_products.differing) > 0:
                resp = self.__send_to_api("patch", "/products/", self.__changed_products.differing)
                if resp['stat'] == 'ok':
                    self.__changed_products.save_differing_to_db()
                    self.__changed_products.clear_differing_data()
                elif resp['stat'] == 'some_imports_failed':
                    self.__changed_products.prepare_resend_after_some_imports_failed_differing(resp['failed_items_id'])

            if len(self.__changed_products.missing) == 0 and len(self.__changed_products.differing) == 0:
                return
            
        raise ApiRequestError("Sending data failed too many times");
        

    def __send_to_api(self, method: str, endpoint: str, data: list[dict]):
        headers = {
            "X-Api-Key": settings.INTEGRATOR_API_KEY, 
            "Content-Type": "application/json"
        }
        response = send_api_request(
            method=method,
            url=f"{settings.INTEGRATOR_API_BASE_URL}{endpoint}",
            data=data,
            headers=headers,
            max_retries=10,
            retry_delay=2,
            timeout=60
        )
        return response
