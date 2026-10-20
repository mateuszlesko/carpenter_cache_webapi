from unittest.mock import Mock, MagicMock

from services.order_data_service import OrderDataService


def test_get_orders_to_confirm():
    mock_redis_repo = Mock()
    mock_redis_repo.get_keys.return_value = [b'order_id:123', b'order_id:456']
    order_data_service = OrderDataService(redis_host='localhost', redis_port=6379, redis_db=0)
    order_data_service._r_repo = mock_redis_repo

    result = order_data_service.get_orders_to_confirm()

    assert result['status'] == 'SUCCESS'
    assert result['message'] == 'orders to confirm are'
    assert result['orders_ids'] == [{'order_id': '123'}, {'order_id': '456'}]


def test_create_existing_order_error():
    mock_redis_repo = Mock()
    mock_redis_repo.get.return_value = {'order_id': '123', 'client_id': '456', 'products': [{'product_id': '789', 'amount': 1}]}
    order_data_service = OrderDataService(redis_host='localhost', redis_port=6379, redis_db=0)
    order_data_service._r_repo = mock_redis_repo

    result = order_data_service.create_order({'client_id': '456', 'products': [{'product_id': '789', 'amount': 1}]})

    assert result['status'] == 'ERROR'
    assert result['message'] == 'order already exists'


def test_create_order_success():
    mock_redis_repo = Mock()
    mock_redis_repo.get.return_value = None
    mock_redis_repo.set.return_value = {'order_id': '123', 'client_id': '456', 'products': [{'product_id': '789', 'amount': 1}]}
    order_data_service = OrderDataService(redis_host='localhost', redis_port=6379, redis_db=0)
    order_data_service._r_repo = mock_redis_repo

    result = order_data_service.create_order({'client_id': '456', 'products': [{'product_id': '789', 'amount': 1}]})

    assert result['status'] == 'SUCCESS'
    assert result['message'] == 'order created'
    assert result['order']['client_id'] == '456'
    assert result['order']['products'] == [{'product_id': '789', 'amount': 1}]
    

def test_create_order_validation_error(mocker):

    order_data_service = OrderDataService(redis_host='localhost', redis_port=6379, redis_db=0)
    
    mocker.patch.object(order_data_service,
    "_validate_order",
    return_value = False)

    result = order_data_service.create_order({'products': [{'product_id': '789', 'amount': 'xyz'}]})

    assert result['status'] == 'ERROR'
    assert result['message'] == 'invalid order'


def test_confirm_order_success(mocker):
    DUMP_ORDER = bytes("""{"order_id": "123", "client_id": "456", "products": [{"product_id": "789", "amount": 1}]}""","utf-8")
    
    mock_redis_repo = Mock()
    mock_redis_repo.get.return_value = DUMP_ORDER
    order_data_service = OrderDataService(redis_host='localhost', redis_port=6379, redis_db=0)
    order_data_service._r_repo = mock_redis_repo

    result = order_data_service.confirm_order('123')

    assert result['status'] == 'SUCCESS'
    assert result['message'] == 'order confirmed'


def test_confirm_order_not_found():
    mock_redis_repo = Mock()
    mock_redis_repo.get.return_value = None
    order_data_service = OrderDataService(redis_host='localhost', redis_port=6379, redis_db=0)
    order_data_service._r_repo = mock_redis_repo

    result = order_data_service.confirm_order('123')

    assert result['status'] == 'ERROR'
    assert result['message'] == 'order not found'