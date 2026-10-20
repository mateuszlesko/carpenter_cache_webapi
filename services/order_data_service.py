import json
import datetime

from repositories.redis_repository import RedisRepository
from utils.order_utils import OrderUtils



class OrderDataService:
    """
    abstraction layer for managaing REDIS cache memory - validating incoming data,
    creating records, deleting
    """    
    
    def __init__(self, redis_host : str, redis_port : int, redis_db : int):
        self._r_repo = RedisRepository(redis_host, redis_port, redis_db)


    def get_orders_to_confirm(self):
        pattern = "order_id:*"
        orders = self._r_repo.get_keys(pattern)
        if orders is None:
            return {'status': 'ERROR', 'message': 'no orders found'}
        orders = [order.decode("utf-8") for order in orders]
        orders = [dict(order_id = order.split(":")[1]) for order in orders]
        return {'status': 'SUCCESS', 'message': 'orders to confirm are', 'orders_ids': orders} 


    def create_order(self, order : dict):

        if not self._validate_order(order):
            return {'status': 'ERROR', 'message': 'invalid order'}
            
        order["order_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        order["order_id"] = OrderUtils.generate_id(order["client_id"], order["order_date"])
        key = "order_id:{}".format(order["order_id"])

        if self._r_repo.get(key) is not None:
            return {'status': 'ERROR', 'message': 'order already exists'}
        
        created_order = self._r_repo.set(key, order)
        if created_order is None:
            return {'status': 'ERROR', 'message': 'order could not be created'}

        return {'status': 'SUCCESS', 'message': 'order created', 'order': order}


    def get_order(self, order_id : str):
        pattern = "order_id:{}".format(order_id)
        order = self._r_repo.get(pattern)
        if order is None:
            return {'status': 'ERROR', 'message': 'order not found'}
        order = json.loads(order.decode("utf-8"))
        return {'status': 'SUCCESS', 'message': 'order retrieved', 'order': order}


    def confirm_order(self, order_id : str):
        pattern = "order_id:{}".format(order_id)
        order = self.get_order(order_id)
        if order["status"] == "ERROR":
            return {'status': 'ERROR', 'message': 'order not found'}

        self._r_repo.delete(pattern)
        return {'status': 'SUCCESS', 'message': 'order confirmed'}


    def _validate_order(self, order : dict):
        
        if "client_id" not in order:
            return False
        if order["products"] is None or len(order["products"]) == 0:
            return False
        for product in order["products"]:
            if "product_id" not in product or "amount" not in product:
                return False
            if not isinstance(product["amount"], int) or product["amount"] <= 0:
                return False
        return True


