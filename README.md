# Skill Mind Map Internet (SMI)

## 1. Product introduction

Skill Mind Map Internet (SMI) is a normalized Skill knowledge base and association engine. It turns a natural-language task into ranked Skill candidates, related Skills, CLI and open-source repository references, and a compact loadout that another agent can actually mount.

SMI is delivered as two coordinated products: a standard-library MCP server and a trigger Skill. The trigger Skill recognizes Skill-discovery intent and tells an agent which MCP tools to call. The MCP performs catalog search, graph recall, loadout construction, and bundled Skill loading. This separation keeps the trigger small while making retrieval reusable from any MCP client.

The catalog currently contains 19,502 records: 19,172 Skill records, 131 CLI records, and 199 open-source repository records.

## 2. Problems it solves

Agents often know how to execute a task but fail to find a reusable Skill before execution. A large collection also makes similar Skills difficult to compare, hides relationships between tools, and wastes context when the whole registry is injected into a prompt.

SMI solves this with normalized records, multiple tags, MTO relationships, IDF-based recall, related-item traversal, and a loadout step. It treats public open-source Skill material as data that must be cleaned, tagged, filtered, merged or split before it becomes a usable index. The result passed downstream is a small set of concrete Skills and related suggestions, not the entire database.

## 3. Usage guide

Start the MCP server over stdio:

~~~bash
python mcp/smi_mcp_server.py
~~~

Register the command in an MCP client and install or reference skill/SKILL.md as the trigger Skill. The trigger flow is:

1. get_catalog_stats when the catalog scope is unknown.
2. search_skills for a natural-language task or keyword.
3. recall_skills when one known Skill needs related Skills.
4. build_loadout to create a compact main-Skill and related-Skill package.
5. load_skill only when a bundled O-type Skill document is needed.

The MCP exposes five tools:

- search_skills searches CLI and repository records by default; pass kinds explicitly when Skill records must be included.
- recall_skills follows the tag and MTO association path from one known Skill.
- build_loadout returns main records, related records, scores, modes, and missing names.
- load_skill reads a bundled O-type document when it exists locally.
- get_catalog_stats reports record counts and graph sizes.

The command-line tools remain available:

~~~bash
python act4_recall.py --search "video conversion"
python act4_recall.py <skill-name> 8
python act4_arm.py <skill-name-1> <skill-name-2> --k 10
~~~

## 4. Notes and boundaries

A recall score ranks candidates; it does not prove that an external Skill, CLI, repository, model, or provider is installed, maintained, or currently available. The catalog counts describe the current index and can change when the public source set is refreshed. Full documents are bundled only for O-type Skills under o_skills/. The loadout builder needs concrete Skill names and is not a replacement for a general-purpose prompt.

SMI uses public or user-provided source material and does not include private memory in the trigger Skill. External mounting is a separate configuration step. The act4_arm.py command writes an armory_loadout.md artifact, so callers should run it in an intended writable directory.

## 5. Technical implementation

The normalized registry is JSONL. The ingestion and recall pipeline performs text normalization, synonym expansion, field-weighted ranking, coverage filtering, IDF recall, tag recall, and related-item traversal. MTO metadata describes M (judgment), T (deterministic execution), and O (orchestration) relationships. edges.json stores the Skill MTO graph; edges_cli.json links CLI and repository records while keeping their scoring domain separate.

mcp/smi_mcp_server.py implements initialize, tools/list, ping, and tools/call over JSON-RPC using only the Python standard library. It reuses the same Recall implementation as act4_recall.py, so CLI and MCP share one catalog and one ranking path. skill/SKILL.md is the external trigger layer: it contains the call sequence and downstream handoff rules, while the MCP owns actual retrieval and loading.

---

# Skill Mind Map Internet（SMI）

## 1. 产品介绍

Skill Mind Map Internet（SMI）是一个标准化的 Skill 知识库和联想引擎。它把自然语言任务转换成排序后的 Skill 候选、相关 Skill、CLI 和开源仓库参考，以及可以真正交给下游智能体装载的精简装载单。

SMI 由两个配套部分组成：标准库 MCP 服务和触发型 Skill。触发型 Skill 识别用户是否需要 Skill 发现，并告诉智能体按什么顺序调用 MCP；MCP 负责目录检索、网络联想、装载单生成和已打包 Skill 读取。触发层保持轻量，检索能力可以被任何 MCP 客户端复用。

当前索引共 19,502 条记录：19,172 条 Skill、131 条 CLI 和 199 条开源仓库记录。

## 2. 解决的痛点

智能体经常会执行任务，却不会在执行前找到可复用的 Skill。库变大后，相似 Skill 难以比较，工具之间的关系不容易被发现，把整个注册表塞进提示词又会浪费上下文。

SMI 使用标准化记录、多标签、MTO 关系、IDF 召回、关联遍历和装载单解决这些问题。公开开源 Skill 先经过数据清洗、打标、筛选、同类合并或拆分，才进入可用索引。下游拿到的是一组具体 Skill 和相关建议，不是整个数据库。

## 3. 使用指南

通过 stdio 启动 MCP：

~~~bash
python mcp/smi_mcp_server.py
~~~

在 MCP 客户端注册这个命令，并安装或引用 skill/SKILL.md 作为触发型 Skill。触发流程是：

1. 目录范围不清楚时调用 get_catalog_stats。
2. 针对自然语言任务或关键词调用 search_skills。
3. 已知某个 Skill、需要找关联时调用 recall_skills。
4. 需要交给下游智能体时调用 build_loadout。
5. 只有必须读取完整 O 型 Skill 时才调用 load_skill。

MCP 提供五个工具：

- search_skills 默认检索 CLI 和仓库记录；需要检索 Skill 时显式传入 kinds。
- recall_skills 从一个已知 Skill 沿标签和 MTO 关系联想。
- build_loadout 返回主记录、关联记录、分数、召回模式和缺失名称。
- load_skill 在本地存在时读取已打包的 O 型 Skill 文档。
- get_catalog_stats 返回记录数量和网络规模。

命令行入口仍然保留：

~~~bash
python act4_recall.py --search "视频转换"
python act4_recall.py <skill-name> 8
python act4_arm.py <skill-name-1> <skill-name-2> --k 10
~~~

## 4. 注意事项

召回分数只用于排序，不证明外部 Skill、CLI、仓库、模型或供应商已经安装、维护或当前可用。索引规模对应当前数据版本，重新收集公开来源后会变化。完整文档只随仓库提供 o_skills/ 下的 O 型 Skill。装载单需要具体 Skill 名称，不能代替通用提示词。

SMI 的触发型 Skill 使用公开或用户提供的来源，不包含个人记忆。外部 Skill 的挂载仍需要单独配置。act4_arm.py 会写入 armory_loadout.md，调用时应放在明确允许写入的目录。

## 5. 技术实现

标准化注册表使用 JSONL。导入和召回流程包含文本规范化、同义词扩展、字段加权排序、覆盖度过滤、IDF 召回、标签召回和关联遍历。MTO 元数据描述 M（判断）、T（确定性执行）和 O（编排）关系。edges.json 保存 Skill 的 MTO 网络，edges_cli.json 连接 CLI 与仓库记录，同时保持独立评分空间。

mcp/smi_mcp_server.py 只使用 Python 标准库，通过 JSON-RPC 实现 initialize、tools/list、ping 和 tools/call。它与 act4_recall.py 共用同一个 Recall 实现，因此 MCP 和 CLI 使用同一索引和排序路径。skill/SKILL.md 是外置触发层，负责调用顺序和下游交接规则；实际检索和装载由 MCP 负责。




