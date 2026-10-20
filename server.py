import os

#external modules import
from flask import Flask, jsonify, request

#standard modules import
from dotenv import load_dotenv

# codebase modules import
from services import OrderDataService
from services import OrderConfirmationKeySubject, OrderConfirmationObserver
from utils.order_utils import OrderUtils

app = Flask(__name__)

load_dotenv()

order_data_service = OrderDataService(os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT'), os.getenv('ORDERS_DB'))
# follow the order confirmation process using the observer pattern
order_confirmation_subject = OrderConfirmationKeySubject()
orders_to_confirm = [
    {
        "client_id": 1,
        "products" : [
            {
                "product_id" : 1,
                "amount" : 1
            },
            {
                "product_id" : 2,
                "amount" : 4
            }
        ]
    },
    {
        "client_id": 2,
        "products" : [
            {
                "product_id" : 2,
                "amount" : 1
            }
        ]
    },
]

for order in orders_to_confirm:
    status = order_data_service.create_order(order)
    if status["status"] == "SUCCESS":
        order_confirmation_observer = OrderConfirmationObserver.create_observer(status['order'])
        order_confirmation_subject.attach(status['order']['order_id'], order_confirmation_observer)
        print(f"SUCCESS: [] Order {order['order_id']}] created successfully")


@app.route('/orders/toconfirm')
def get_orders_to_confirm():

    orders_to_confirm = order_data_service.get_orders_to_confirm()
    return jsonify(orders_to_confirm)


@app.route('/orders/create', methods=['POST'])
def create_order():
    order = request.get_json()

    create_try_counter = 0
    status = order_data_service.create_order(order)

    while create_try_counter < 3 and status["status"] == "ERROR":
        status = order_data_service.create_order(order)
        create_try_counter += 1
        if status["status"] == "SUCCESS":
            break
     
    if status["status"] == "SUCCESS":
        order_id = status["order"]["order_id"]
        order_confirmation_observer = OrderConfirmationObserver.create_observer(status["order"])
        order_confirmation_subject.attach(order_id, order_confirmation_observer)
        print(f"SUCCESS: Order {order_id} created successfully and observer attached")
    return jsonify(status)


@app.route('/subjects', methods=['GET'])
def get_subjects():
    return jsonify({'subjects': order_confirmation_subject.get_subjects()})


@app.route('/orders/status/<string:order_id>', methods=['GET'])
def get_order_status(order_id):
    return order_data_service.get_order(order_id)


@app.route('/orders/confirm/<string:order_id>', methods=['GET'])
def confirm_order(order_id):
    
    order = order_data_service.get_order(order_id)
    if order["status"] == "ERROR":
        return jsonify({'status': 'ERROR', 'message': 'order not found'})
    
    # send to main db order via grpc
    order_confirmation_subject.confirm_order(order["order"]["order_id"])
    order_confirmation_subject.detach(order_id)

    # if success then delete order from cache
    deletion = order_data_service.confirm_order(order_id)
    if deletion["status"] == "ERROR":
        return jsonify({'status': 'ERROR', 'message': 'order could not be confirmed'}) 

    order_confirmation_subject.detach(order_id)
    
    return jsonify({'status': 'SUCCESS', 'message': 'order confirmed'})


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"