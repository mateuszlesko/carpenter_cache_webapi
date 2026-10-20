from unittest.mock import Mock, MagicMock

from services.order_observer_service import OrderConfirmationObserver, OrderConfirmationKeySubject



DUMP_ORDER = {
    "order_id" : "123", 
    "client_id" : "123", 
    "products" : [
        {
            "product_id" : "123",
            "ammount" : 1
        }
    ]
}


def test_create_observer():
    dump_order = {
        "order_id" : "123", 
        "client_id" : "123", 
        "products" : [
            {
                "product_id" : "123",
                "ammount" : 1
            }
        ]
    }

    order_observer = OrderConfirmationObserver.create_observer(dump_order)
    assert order_observer.order["order_id"] == dump_order["order_id"]


def test_order_observer_update():
    pass


def test_attach_observer_to_subject_success():

    grpc_mock = Mock()
    subject = OrderConfirmationKeySubject()

    observer_1 = OrderConfirmationObserver.create_observer(DUMP_ORDER)
    observer_2 = OrderConfirmationObserver.create_observer(DUMP_ORDER)

    observer_1.grpc_service = grpc_mock
    observer_2.grpc_service = grpc_mock

    subject.attach("abc", observer_1)
    subject.attach("abc", observer_2)

    assert ["abc"] == subject.get_subjects()
    
    assert OrderConfirmationKeySubject.count_observers("abc") == 2

    subject.confirm_order("abc")

    subject.detach("abc")




def test_fail_notify_observers():
    subject = OrderConfirmationKeySubject()
    subject.notify('xyz')