"""E-commerce support tools over MCP. Role-agnostic: Sentinel's gateway enforces RBAC."""
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sentinel-ecommerce")
DB = json.loads((Path(__file__).parent / "data.json").read_text())


@mcp.tool()
def track_order(order_id: str) -> str:
    """Get shipping status for an order ID (e.g. 5001)."""
    o = DB["orders"].get(order_id)
    return json.dumps(o) if o else f"No order {order_id}."


@mcp.tool()
def lookup_customer(customer_id: str) -> str:
    """Look up a customer profile by customer ID (e.g. C1). Agents and above."""
    c = DB["customers"].get(customer_id.upper())
    return json.dumps(c) if c else "Customer not found."


@mcp.tool()
def issue_refund(order_id: str, amount: str) -> str:
    """Issue a refund on an order. Supervisors and above."""
    if order_id not in DB["orders"]:
        return f"No order {order_id}."
    return json.dumps({"refund_id": f"RFD-{order_id}", "order_id": order_id, "amount": amount, "status": "approved"})


@mcp.tool()
def get_margin_report() -> str:
    """Get confidential product margin data. Admin only."""
    return json.dumps(DB["margins"])


if __name__ == "__main__":
    mcp.run()
