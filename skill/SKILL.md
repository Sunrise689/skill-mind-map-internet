---
name: skill-mind-map-internet-trigger
description: Trigger SMI when a task needs Skill discovery, related Skill recall, MTO routing, or a compact Skill loadout.
---

# Skill Mind Map Internet Trigger

Use this Skill when the user asks for SMI, Skill Mind Map Internet, Skill 思维库, suitable Skills for a task, related Skill recall, MTO routing, or a Skill loadout.

## Call sequence

1. Call `get_catalog_stats` when the catalog scope is unclear.
2. Call `search_skills` for a natural-language task or keywords.
3. Call `recall_skills` when a known Skill needs related Skills.
4. Call `build_loadout` to produce the small set of main Skills and related suggestions for a downstream agent.
5. Call `load_skill` only for a bundled O-type Skill that must be read in full.

Pass concrete Skill names and relevant excerpts to the downstream task. Do not pass the whole registry as context. Treat search scores as ranking suggestions and keep the returned evidence and limitations visible.

## MCP entry

Run `python mcp/smi_mcp_server.py` as a stdio MCP server. The trigger Skill supplies the intent and call order. The MCP owns catalog search, graph recall, loadout construction, and bundled Skill loading.
