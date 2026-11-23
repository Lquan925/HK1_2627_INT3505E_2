from uuid import uuid4


def v1_create_order(body):
    return {
        "order_id": uuid4().hex,
        "account_id": body["account_id"],
        "status": "created",
        "version": "v1",
    }


def v2_create_order(body):
    return {
        "order_id": uuid4().hex,
        "account_id": body["account_id"],
        "status": "created",
        "version": "v2",
        "processing": "enhanced",
    }
