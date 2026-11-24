"""One Lambda serving several MCP tools behind AgentCore Gateway.

Gateway invokes the function with the tool arguments as the event and puts the tool name in
context.client_context.custom["bedrockAgentCoreToolName"] as "<target-name>___<tool-name>".
"""
import json

ORDERS = {"A-1001": {"status": "SHIPPED", "carrier": "UPS"}, "A-1002": {"status": "DELIVERED", "carrier": "DHL"}}
INVENTORY = {"SKU-1": 42, "SKU-2": 0}


def get_order(event):
    oid = str(event.get("order_id", "")).upper()
    return ORDERS.get(oid) or {"error": f"order {oid} not found"}


def check_stock(event):
    sku = str(event.get("sku", "")).upper()
    return {"sku": sku, "available": INVENTORY.get(sku, 0)}


def issue_refund(event):
    # Business logic only. WHO may refund HOW MUCH is enforced outside this code by AgentCore Policy (Lab 30).
    return {"refund_id": f"RF-{event.get('order_id')}", "amount": event.get("amount"), "status": "ISSUED"}


TOOLS = {"get_order": get_order, "check_stock": check_stock, "issue_refund": issue_refund}


def lambda_handler(event, context):
    full = (context.client_context.custom or {}).get("bedrockAgentCoreToolName", "") if context.client_context else ""
    tool = full.split("___", 1)[-1]
    fn = TOOLS.get(tool)
    if fn is None:
        return {"error": f"unknown tool {full!r}"}
    return fn(event if isinstance(event, dict) else json.loads(event))
