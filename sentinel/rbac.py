"""Role-based access control driven by the domain config. Roles are listed
lowest to highest privilege. Enforced at retrieval, tool exposure, tool
execution (defense in depth) and the cache."""
from sentinel import domain


def level(role: str, cfg: dict | None = None) -> int:
    roles = (cfg or domain.current())["roles"]
    if role not in roles:
        raise ValueError(f"unknown role: {role}")
    return roles.index(role)


def can_read(role: str, min_role: str, cfg: dict | None = None) -> bool:
    return level(role, cfg) >= level(min_role, cfg)


def can_use_tool(role: str, tool: str, cfg: dict | None = None) -> bool:
    cfg = cfg or domain.current()
    need = cfg["tools"].get(tool)
    return need is not None and level(role, cfg) >= level(need, cfg)   # unknown tools denied


def allowed_tools(role: str, tools: list[dict], cfg: dict | None = None) -> list[dict]:
    return [t for t in tools if can_use_tool(role, t["function"]["name"], cfg)]
