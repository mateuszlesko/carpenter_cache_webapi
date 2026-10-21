import logging
import os

import grpc

from proto.build.proto import user_product_order_pb2, user_product_order_pb2_grpc

_LOGGER = logging.getLogger(__name__)


class OrderGrpcService:
    """
    GRPC client logic for sending order confirmation to store api
    """


    def __init__(self, host_server, port):
        self.channel = grpc.insecure_channel(
                "{}:{}".format(host_server, port)
            )

    def confirm_order(self, order: dict) -> None:
        """
        act as a client, send a GRPC request to the server with order's data that needs to be saved as confirmed
        """
        try:
            stub = user_product_order_pb2_grpc.UserProductOrderStub(self.channel)
            request = user_product_order_pb2.UserProductOrderRequest(
                order_id=str(order["order_id"]),
                client_id=str(order["client_id"]),
                products= [
                user_product_order_pb2.ProductOrder(
                    product_id=str(item["product_id"]),
                    unit=int(item["amount"]),
                )
                for item in order.get("products", [])
                ]
            )

            response = stub.ConfrimUserProductOrder(request)
            print("Call success: %s", response)
            _LOGGER.info("Call success: %s", response)
        except grpc.RpcError as grpc_error:
            print("ERROR: Call failed ", grpc_error)
            _LOGGER.error("Call failure: %s", grpc_error)