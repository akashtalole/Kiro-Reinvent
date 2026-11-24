"""Domain tools for the Acme Orders support agent (in-memory fake backend).

Reused by Labs 22–26 and the end-to-end customer-support build (Lab 34).
"""
from __future__ import annotations

from datetime import date, timedelta

from strands import tool

_ORDERS = {
    "A-1001": {"customer": "c-42", "status": "SHIPPED", "carrier": "UPS", "eta": str(date.today() + timedelta(days=2)), "total": 129.00},
    "A-1002": {"customer": "c-42", "status": "DELIVERED", "carrier": "DHL", "eta": str(date.today() - timedelta(days=3)), "total": 59.90},
    "A-1003": {"customer": "c-77", "status": "PROCESSING", "carrier": None, "eta": None, "total": 15.00},
}
REFUND_WINDOW_DAYS = 30


@tool
def get_order(order_id: str) -> dict:
    """Look up an order by id.

    Args:
        order_id: Order identifier such as "A-1001".

    Returns:
        The order's status, carrier, ETA and total, or an error if not found.
    """
    order = _ORDERS.get(order_id.strip().upper())
    return {"order_id": order_id, **order} if order else {"error": f"order {order_id} not found"}


@tool
def list_orders(customer_id: str) -> list[dict]:
    """List all orders for a customer.

    Args:
        customer_id: Customer identifier such as "c-42".
    """
    return [{"order_id": oid, **o} for oid, o in _ORDERS.items() if o["customer"] == customer_id]


@tool
def check_refund_eligibility(order_id: str) -> dict:
    """Decide whether an order can be refunded under the 30-day policy.

    Only DELIVERED orders delivered within the last 30 days are eligible.

    Args:
        order_id: Order identifier.
    """
    order = _ORDERS.get(order_id.strip().upper())
    if not order:
        return {"eligible": False, "reason": "order not found"}
    if order["status"] != "DELIVERED":
        return {"eligible": False, "reason": f"status is {order['status']}; refunds apply to delivered orders"}
    delivered = date.fromisoformat(order["eta"])
    days = (date.today() - delivered).days
    eligible = days <= REFUND_WINDOW_DAYS
    return {"eligible": eligible, "days_since_delivery": days, "amount": order["total"] if eligible else 0}
