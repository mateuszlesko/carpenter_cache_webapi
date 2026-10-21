# Carpenter cache webapi

## About

`Carpenter cache webapi` is a mircoservice which acts primary as a cache for orders that needs to be confirmed by the clients. WebAPI works also as a gate to internal backend services which are procceding further workshop orders.


## Software Architecture

```mermaid
flowchart LR
    C[Client] -->|HTTP POST /orders/create`| A[Carpenter Cache API]
    C -->|HTTP GET /confirm_order/${order_id}| A

    A -->|gRPC request| O[Carpenter Orders API]

    A -->|Response| C
    O -->|Order confirmation / result| A
```

### Description

- The client communicates with the Carpenter Cache API over HTTP.
- For order creation:
  - `POST /orders/create`. The data is stored in Redis DB till it is confirmed
- For confirmation:
  - `GET /confirm_order/${order_id}`
- The Carpenter Cache API then forwards the order data to the Carpenter Orders API using gRPC.

### Flow

1. Client sends an HTTP `POST` request to `/orders/create` on the Carpenter Cache API.
2. Client sends an HTTP `GET` request to `/confirm_order/${order_id}` on the Carpenter Cache API.
3. The Carpenter Cache API sends order data as gRPC call to the Carpenter Orders Management System API.
4. The Orders API returns the order status or confirmation.
5. The Carpenter Cache API sends the result back to the client.


### How to run:

#### Before run - depedencies:
- Docker with Composer installed on your host
- cloned and already running `CarpenterOrdersManagmentSystem`
- .env file


`.env` file example:

```
export APP_PORT=8000
export APP_HOST=0.0.0.0
export APP_EXPOSED_PORT=8000
export REDIS_HOST=redis
export REDIS_PORT=6379
export ORDERS_DB=0
export GRPC_SUB_PORT=5246
export CARPENTER_STORE_API=carpenterordersmanagmentsystem-web-1
```

### Deploy:

In terminal run the following command:
```source tools/build_run.sh --run dev
```