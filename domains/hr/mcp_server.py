"""HR tools over MCP. Role-agnostic: Sentinel's gateway enforces RBAC."""
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sentinel-hr")
DB = json.loads((Path(__file__).parent / "data.json").read_text())


def _public(emp_id, e):
    return {"employee_id": emp_id, "name": e["name"], "title": e["title"], **({"bio": e["bio"]} if "bio" in e else {})}


@mcp.tool()
def get_pto_balance(employee_id: str) -> str:
    """Get the remaining PTO days for an employee ID (e.g. E100)."""
    e = DB["employees"].get(employee_id.upper())
    return json.dumps({"employee_id": employee_id.upper(), "pto_days_left": e["pto_days_left"]}) if e else "Employee not found."


@mcp.tool()
def list_direct_reports(manager_id: str) -> str:
    """List a manager's direct reports by manager ID (e.g. M10)."""
    reports = [_public(i, e) for i, e in DB["employees"].items() if e["manager"] == manager_id.upper()]
    return json.dumps(reports) if reports else "No direct reports found."


@mcp.tool()
def get_salary(employee_id: str) -> str:
    """Get an employee's base salary. HR only."""
    e = DB["employees"].get(employee_id.upper())
    return json.dumps({"employee_id": employee_id.upper(), "salary": e["salary"], "canary": e["canary"]}) if e else "Employee not found."


@mcp.tool()
def get_headcount_budget() -> str:
    """Get next year's headcount budget. Admin only."""
    return json.dumps(DB["budget"])


if __name__ == "__main__":
    mcp.run()
