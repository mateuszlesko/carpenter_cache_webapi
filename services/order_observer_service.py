""" build-in imports """
import logging
import os


from .grpc.order_grpc_service import OrderGrpcService
from .observer import Subject, SubjectKey, Observer

_LOGGER = logging.getLogger(__name__)

"""
logic for informing internal software components about 
an order confirmation event occuring
"""

class OrderConfirmationObserver(Observer):
    
    def __init__(self):
        self.order = None
        self.grpc_service = OrderGrpcService(os.getenv("CARPENTER_STORE_API"), os.getenv("GRPC_SUB_PORT"))


    @staticmethod
    def create_observer(order: dict) -> "OrderConfirmationObserver":
        observer = OrderConfirmationObserver()
        observer.order = order
        observer.grpc_service = OrderGrpcService(os.getenv("CARPENTER_STORE_API"), os.getenv("GRPC_SUB_PORT"))
        return observer


    def update(self) -> None:
        self.grpc_service.confirm_order(self.order)
        _LOGGER.info("Order confirmation sent to gRPC service for order_id: %s", self.order['order_id'])


class OrderConfirmationKeySubject(Subject):

    __observers: dict[str, list[OrderConfirmationObserver]] = {}

    @staticmethod
    def count_observers(key):
        return len(__class__._observers[key])


    def attach(self, key: str, observer: OrderConfirmationObserver) -> None:
        if key not in self.__observers.keys():
            self.__observers[key] = []
        self.__observers[key].append(observer)


    def detach(self, key: str)-> None:
        if key in __class__.__observers.keys():
            __class__.__observers.pop(key, None)


    def notify(self, key) -> None:
        observers = self.__observers.get(key)
        if observers:
            for observer in observers:
                observer.update()


    def confirm_order(self, order_id: str) -> None:
        self.notify(order_id)


    def get_subjects(self) -> list[str]:
        return list(self.__observers.keys())

