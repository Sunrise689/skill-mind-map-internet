"""SMI MCP server: searchable Skill catalog, recall graph, and loadout builder."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from act4_recall import Recall  # noqa: E402

REGISTRY = ROOT / "registry_networked.jsonl"
EDGES = ROOT / "edges.json"
EDGES_CLI = ROOT / "edges_cli.json"
_RECALL = Recall(REGISTRY)

TOOLS = [
    {"name": "search_skills", "description": "Search SMI Skill, CLI, and repository records by task terms.", "inputSchema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}, "kinds": {"type": "array", "items": {"type": "string"}}}}},
    {"name": "recall_skills", "description": "Recall related records from one mounted Skill using the SMI graph and tag index.", "inputSchema": {"type": "object", "required": ["skill_name"], "properties": {"skill_name": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}}}},
    {"name": "build_loadout", "description": "Build a compact main-Skill and related-Skill loadout for a task.", "inputSchema": {"type": "object", "required": ["skill_names"], "properties": {"skill_names": {"type": "array", "items": {"type": "string"}}, "limit": {"type": "integer", "minimum": 1, "maximum": 20}}}},
    {"name": "load_skill", "description": "Load one bundled O-type Skill document when it is present in this product.", "inputSchema": {"type": "object", "required": ["skill_name"], "properties": {"skill_name": {"type": "string"}}}},
    {"name": "get_catalog_stats", "description": "Return catalog counts and MTO graph summary.", "inputSchema": {"type": "object", "properties": {}}},
]


def _stats() -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in _RECALL.rows:
        kind = row.get("kind") or "skill"
        counts[kind] = counts.get(kind, 0) + 1
    edges = json.loads(EDGES.read_text(encoding="utf-8")) if EDGES.exists() else {}
    cli_edges = json.loads(EDGES_CLI.read_text(encoding="utf-8")) if EDGES_CLI.exists() else {}
    return {"records": sum(counts.values()), "by_kind": counts, "mto": {"keys": sorted(edges)[:20], "edge_records": len(edges.get("edges", [])) if isinstance(edges, dict) else 0}, "cli_graph": {"edge_records": len(cli_edges.get("edges", [])) if isinstance(cli_edges, dict) else 0}}


def _loadout(names: list[str], limit: int) -> dict[str, Any]:
    mains = []
    missing = []
    for name in names:
        row = _RECALL.by_name.get(name)
        if row is None:
            missing.append(name)
            continue
        mains.append({"name": name, "kind": row.get("kind") or "skill", "description": row.get("desc"), "tags": row.get("tags", [])[:8]})
    related: list[dict[str, Any]] = []
    seen = {x["name"] for x in mains}
    for main in names:
        if main not in _RECALL.by_name:
            continue
        mode, rows = _RECALL.recall(main, limit)
        for name, score in rows:
            if name in seen:
                continue
            seen.add(name)
            row = _RECALL.by_name.get(name, {})
            related.append({"name": name, "score": round(score, 3), "mode": mode, "kind": row.get("kind") or "skill", "description": row.get("desc"), "tags": row.get("tags", [])[:8]})
    return {"main": mains, "related": related, "missing": missing}


def _call(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "search_skills":
        query = str(args.get("query", "")).strip()
        if not query:
            raise ValueError("query is required")
        kinds = tuple(args.get("kinds") or ("cli", "repo"))
        return {"query": query, "results": _RECALL.search(query, int(args.get("limit", 10)), kinds=kinds)}
    if name == "recall_skills":
        skill_name = str(args.get("skill_name", "")).strip()
        if not skill_name:
            raise ValueError("skill_name is required")
        mode, rows = _RECALL.recall(skill_name, int(args.get("limit", 10)))
        return {"skill_name": skill_name, "mode": mode, "results": [{"name": n, "score": round(s, 3)} for n, s in rows]}
    if name == "build_loadout":
        names = args.get("skill_names")
        if not isinstance(names, list) or not names:
            raise ValueError("skill_names must be a non-empty array")
        return _loadout([str(x) for x in names], int(args.get("limit", 10)))
    if name == "load_skill":
        skill_name = str(args.get("skill_name", "")).strip()
        path = ROOT / "o_skills" / skill_name / "SKILL.md"
        if not path.is_file():
            return {"skill_name": skill_name, "available": False, "message": "This Skill is indexed but its full document is not bundled in this product."}
        return {"skill_name": skill_name, "available": True, "content": path.read_text(encoding="utf-8")}
    if name == "get_catalog_stats":
        return _stats()
    raise ValueError(f"unknown tool: {name}")


def _response(request_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        body["error"] = error
    else:
        body["result"] = result
    return body


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return _response(request_id, {})
    if method == "initialize":
        return _response(request_id, {"protocolVersion": message.get("params", {}).get("protocolVersion", "2025-06-18"), "capabilities": {"tools": {}}, "serverInfo": {"name": "skill-mind-map-internet", "version": "1.0.0"}})
    if method == "tools/list":
        return _response(request_id, {"tools": TOOLS})
    if method == "tools/call":
        params = message.get("params", {})
        try:
            result = _call(str(params.get("name", "")), params.get("arguments") or {})
            return _response(request_id, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}], "isError": False})
        except Exception as exc:
            return _response(request_id, {"content": [{"type": "text", "text": json.dumps({"error": str(exc)}, ensure_ascii=False)}], "isError": True})
    return _response(request_id, error={"code": -32601, "message": "Method not found"})


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            result = handle(message)
            if result is not None:
                print(json.dumps(result, ensure_ascii=False), flush=True)
        except Exception as exc:
            print(json.dumps(_response(None, error={"code": -32603, "message": str(exc)}), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
