import hashlib
import random
from ast import literal_eval


class OrderUtils:

    @staticmethod
    def generate_id(client_id, order_date):
        seed = OrderUtils.generate_seed()
        order_hash = f"{client_id}-{seed}-{order_date}".encode("utf-8")
        return str(hashlib.shake_256(order_hash).hexdigest(20))

    @staticmethod
    def generate_seed():
        return random.randint(100000, 999999)

    @staticmethod
    def create_order_dict(dict_string: str) -> dict:
        return literal_eval(dict_string)