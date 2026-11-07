# Skill Mind Map Internet

## Product overview

Skill Mind Map Internet (SMI) is a searchable Skill knowledge base and association engine. It turns a natural-language task into ranked Skills, related Skills, executable CLI or repository suggestions, and a compact loadout that can be passed to another agent.

SMI is delivered as two coordinated parts. The MCP server exposes the catalog and graph through stable tools. The trigger Skill detects SMI-related intent and tells an agent which MCP tools to call. The trigger Skill is the entry point, and the MCP server performs the actual retrieval.

## The problem it solves

Agents often know how to execute a task but fail to find the right reusable Skill before they start. A large Skill collection also creates three practical problems. Similar Skills are difficult to compare, related Skills remain hidden, and handing the whole collection to an agent wastes context.

SMI addresses these problems with a normalized registry, tags, MTO relationships, IDF-based recall, CLI and repository links, and a loadout step that selects a small set of concrete Skills.

## Usage guide

Start the MCP server over stdio.

```bash
python mcp/smi_mcp_server.py
```

Register that command in an MCP client and install or reference `skill/SKILL.md` as the trigger Skill. The MCP provides these tools.

- `search_skills` searches Skill, CLI, and repository records.
- `recall_skills` finds records related to one known Skill.
- `build_loadout` creates a main-Skill and related-Skill package for a downstream task.
- `load_skill` reads a bundled O-type Skill when its full document is included.
- `get_catalog_stats` reports catalog and graph scope.

The original command-line entry points remain available.

```bash
python act4_recall.py --search "video conversion"
python act4_recall.py <skill-name> 8
python act4_arm.py <skill-name-1> <skill-name-2> --k 10
```

## Notes

The current index contains 19,502 records. The stated scope is 19,172 Skills, 131 CLI records, and 199 open-source repository records. Search scores rank candidates and do not certify that an external Skill, CLI, repository, model, or provider is currently installed or available. Full Skill documents are bundled only for the O-type documents under `o_skills/`. External Skill sources can be connected through configuration when required.

## Technical implementation

The catalog is stored as JSONL. `act4_recall.py` implements tokenization, synonym expansion, field-weighted ranking, coverage filtering, IDF recall, and related-item traversal. `edges.json` stores the MTO graph. `edges_cli.json` connects executable CLI and repository records without mixing their scoring semantics with Skill records.

`mcp/smi_mcp_server.py` is a Python standard-library JSON-RPC server that implements the MCP initialize, tools/list, ping, and tools/call methods. It reuses the same `Recall` implementation as the CLI, so MCP and command-line results share one catalog and one ranking path. `skill/SKILL.md` is the trigger layer and contains no private memory or fixed workstation path.

---

# Skill Mind Map Internet（SMI）

## 产品介绍

Skill Mind Map Internet 是一个可检索的 Skill 知识库和联想引擎。它把自然语言任务转换成排序后的 Skill、相关 Skill、CLI 或开源仓库建议，以及可以交给其他智能体的精简 Skill 装载单。

SMI 由两个配套部分组成。MCP 服务提供目录和网络能力，触发型 Skill 识别用户意图并指导调用顺序。触发型 Skill 负责入口，MCP 负责实际检索。

## 解决的痛点

智能体经常会执行任务，却不会在开始前找到最合适的可复用 Skill。Skill 数量变大后，相似 Skill 难以比较，关联 Skill 不容易被发现，把整个库塞进上下文又会浪费大量空间。

SMI 通过标准化索引、标签、MTO 关系、IDF 联想召回、CLI 与仓库关联，以及小规模装载单解决这些问题。

## 使用指南

```bash
python mcp/smi_mcp_server.py
```

在 MCP 客户端注册这个 stdio 服务，并安装或引用 `skill/SKILL.md` 触发型 Skill。MCP 提供以下工具：

- `search_skills`：检索 Skill、CLI 和仓库记录。
- `recall_skills`：从一个已知 Skill 联想相关 Skill。
- `build_loadout`：生成主 Skill 和相关 Skill 装载单。
- `load_skill`：读取仓库内完整的 O 型 Skill。
- `get_catalog_stats`：查看索引和网络规模。

命令行入口仍然保留。

```bash
python act4_recall.py --search "视频转换"
python act4_recall.py <skill-name> 8
python act4_arm.py <skill-name-1> <skill-name-2> --k 10
```

## 注意事项

当前索引共 19,502 条记录，包含 19,172 条 Skill、131 条 CLI 和 199 条开源仓库记录。召回分数用于排序，不代表外部 Skill、CLI、仓库、模型或供应商当前一定已安装或可用。完整 Skill 只随仓库提供 `o_skills/` 下的 O 型文档。需要其他 Skill 时通过配置接入外部正本。

## 技术实现

索引采用 JSONL。`act4_recall.py` 实现分词、同义词扩展、字段加权、覆盖度过滤、IDF 召回和关联遍历。`edges.json` 保存 MTO 网络，`edges_cli.json` 连接 CLI 与仓库记录，同时保持它们和 Skill 记录的评分口径独立。

`mcp/smi_mcp_server.py` 使用 Python 标准库实现 JSON-RPC MCP 服务，支持 initialize、tools/list、ping 和 tools/call。MCP 与命令行共用同一个 `Recall` 实现，因此使用同一个索引和排序逻辑。`skill/SKILL.md` 是触发层，不包含个人记忆或固定本机路径。
