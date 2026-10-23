# 宿主适配与本地盘点

## Codex 优先

先用当前会话技能目录，它包含真实调用名与插件路径。官方文档描述 Codex 从项目和用户的 `.agents/skills` 发现技能，支持符号链接，并可在 Codex 配置的 `skills.config` 中禁用条目。本机及部分发行版也使用 `$CODEX_HOME/skills` 或 `~/.codex/skills`；盘点脚本兼顾这些位置。

不要把整个插件缓存直接当作已启用技能库。会话已经提供的插件技能可直接参与推荐；若清单缺失，通过宿主提供的插件清单/工具能力核实。确有必要时把确定的插件技能目录传给 `--root`，并保留其完整命名空间。

用户在提出任务时选中、附加或通过 `$skill-selector` 调用本技能，就应先进入技能选择环节，不要求用户再表达“推荐技能”的意愿。也可以在用户明确请求选择技能时按描述匹配。它不是钩子或后台常驻路由器。安装新文件不代表本次运行的初始清单已更新；查看宿主技能列表，必要时刷新/新开会话。不要自行修改 `AGENTS.md` 来接管所有请求。

官方依据（2026-10-24 核对）：[Build skills](https://learn.chatgpt.com/docs/build-skills)。实际会话的可用目录优先于静态路径假设。

## 无依赖盘点脚本

需要 Python 3.11+。`<skill-dir>` 是本技能实际所在文件夹，`<task-cwd>` 是用户任务目录；宿主可能将 shell 放在技能目录，必须显式传任务目录以免盘错项目。命令中路径独立引用；用户任务文本通过结构化参数或正确的 shell 引号传递，不能拼接成可执行代码。

```text
python "<skill-dir>/scripts/inventory.py" --agent codex --cwd "<task-cwd>"
python "<skill-dir>/scripts/inventory.py" --agent codex --cwd "<task-cwd>" --query "科研论文汇报 PPT" --top 15
python "<skill-dir>/scripts/inventory.py" --agent codex --root "<verified-plugin-skill-dir>"
python "<skill-dir>/scripts/inventory.py" --only-roots --root "<custom-skill-library>"
```

Windows 中 `python` 不可用时，选用宿主已提供的 Python 绝对路径或本机现有 Python。没有 Python 就用文件工具读取元数据，不安装运行环境来阻塞路由。

输出是 UTF-8 JSON：

- `skills`：原名、完整描述、路径、稳定 ID、来源、`disk_only` 状态；同名不同路径保留。
- `warnings`：不可读/畸形元数据、显式目录缺失、解析限制等，不声称清单完整。
- `excluded_disabled`：Codex 本地配置明确禁用而被排除的数量。
- `excluded_self`：排除本选择器自身的数量，避免自路由。
- `total_skills`：过滤后技能总数；`returned_skills`：本次返回数量。
- `retrieval`：不带查询返回全部；带查询仅做中英文词面召回，绝不表示语义评测或自动执行。

脚本不联网、不写缓存、不读取正文执行、不运行技能代码、不扫描整块硬盘。它只解析常见 YAML 字符串写法；不支持锚点/别名、标签等复杂 YAML，发现时警告而不臆造内容。默认忽略系统中不存在的约定目录，只报告实际检查结果。目录循环及文件数量受限；遇到扫描上限时警告，不能当作穷尽。

本地配置只能补充证据。插件启用状态、账号权限和实际工具可用性仍需宿主核实；不能把 `disk_only` 改称宿主已加载。

## 其他 Agent

通用部分只需要宿主能读取 `SKILL.md` 和其他本地文件。可选脚本的目录预设如下；它们是盘点线索，不是其他客户端的加载保证。

| `--agent` | 默认本地线索 |
| --- | --- |
| `codex`（默认） | 用户/项目 `.agents/skills`、Codex home `skills`、项目 `.codex/skills`、Unix `/etc/codex/skills` |
| `claude` | 用户/项目 `.claude/skills` 和用户/项目 `.agents/skills` |
| `gemini` | 用户/项目 `.gemini/skills` 和用户/项目 `.agents/skills` |
| `all` | 合并以上目录，但不能据此推断跨宿主可调用 |

工作目录向上遍历到最近的 `.git` 标记；不存在 Git 标记时仅检查工作目录，避免把任意父目录里的技能混入当前项目。目录可为 Git 工作树的 `.git` 文件。

安装时将整个 `skill-selector` 文件夹放入目标宿主认可的技能目录。其他宿主可忽略 `agents/openai.yaml`；它仅提供 Codex 界面信息，未声明任何必需厂商工具。使用宿主实际支持的调用语法，不把 Codex 的 `$` 或某客户端的 `/` 当作通用 API。交互工具不可用时，用编号列表提问并结束回合等用户回复。
