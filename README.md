<div align="center">

# 🧭 SP_skill-dynamic_selector

### 任务开始前，让合适的 Skills 先到位

**描述任务 → 罗列大概率用到的技能 → 用户选择 → 再开始执行。**

简体中文 · [English](README.en.md)

[![Agent Skill](https://img.shields.io/badge/Agent-Skill-4F46E5)](SKILL.md)
[![Codex First](https://img.shields.io/badge/Codex-First-111827)](#快速开始)
[![Local First](https://img.shields.io/badge/Local-First-0F766E)](#本地优先与使用边界)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](scripts/inventory.py)
[![Tests](https://github.com/Stephen-studying/SP_skill-dynamic_selector/actions/workflows/tests.yml/badge.svg)](https://github.com/Stephen-studying/SP_skill-dynamic_selector/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B)](LICENSE)

[为什么需要它](#为什么需要它) · [使用示例](#一次真实形态的选择) · [快速开始](#快速开始) · [安装](#安装与分发) · [兼容性](#agent-兼容性) · [验证](#实现与验证)

</div>

![SP Skill Dynamic Selector — select skills before execution](assets/banner.svg)

## 为什么需要它

电脑里装了很多好用的技能，但接到任务时，Agent 仍可能直接动手，漏掉更合适的专业流程。用户也很难记住每个技能负责什么、什么时候该用。

Codex 优先的通用 Agent Skill。提出任务时选中它，就会先进入技能选择环节：分析完整任务，罗列本次大概率会用到的本地技能，覆盖主流程和实际相关的辅助环节，不设固定展示数量上限，等用户选定后再正式执行。无需额外要求“推荐技能”。

本项目把“用哪些技能”变成正式执行前的一步。**你不必先知道技能名称，也不必额外说“请推荐 Skill”。**

| 你遇到的情况 | 选择器会怎样处理 |
| --- | --- |
| 技能太多，记不住名字 | 结合当前任务和可用目录，列出大概率用到的技能 |
| 几个技能看起来很相似 | 说明输入、产物、阶段和替代关系 |
| 一个任务需要多个环节配合 | 列出主流程、辅助环节及建议组合 |
| 相关技能超过四个 | 按实际任务罗列，不截断成固定数量 |
| 希望自己决定执行方式 | 展示清单后等待选择，再读取所选技能并执行 |

## 一次真实形态的选择

**你选中 `skill-selector`，然后输入：**

> 根据这篇工程论文做组会汇报 PPT，包含方法路线图和关键图表解读。

**Agent 先展示类似清单，而不是立即制作文件：**

| 编号 | 任务环节 | 本地技能示例 | 本次用途 | 选择关系 |
| --- | --- | --- | --- | --- |
| 1 | 源材料读取 | `pdf:pdf` | 读取 PDF 的文本、图表与页面结构 | 基础支撑，可能由主技能覆盖 |
| 2 | 论文理解 | `nature-paper-card` | 拆解方法、证据链与局限 | 辅助，也可先做精读 |
| 3 | 学术汇报 | `nature-paper2ppt` | 组织论文叙事，制作中文学术 PPTX | 主流程候选 |
| 4 | 演示制作 | `ppt-master` | 制作或调整可编辑演示文稿 | 与其他制稿路线择一或按需配合 |
| 5 | 演示制作 | `presentations:Presentations` | 创建、编辑演示文稿 | 另一条制稿路线 |
| 6 | 方法可视化 | `tech-route-maker` | 将论文方法整理为可编辑路线图 | 本例明确需要的辅助环节 |
| 7 | 图表处理 | `nature-figure` | 必要时重绘科研图表 | 有原始数据且需要重绘时使用 |

**你回复：** `使用 3+6，需要时再用 1。`

**Agent 随后加载所选技能，按其具体说明完成任务。**

> 这是交互形态示例，假设用户已安装并启用这些技能。实际清单随任务与本地目录动态变化，不固定这些名字，不把所有示例项都列为必选。

## 核心能力

| 能力 | 实际行为 |
| --- | --- |
| 选中即启动 | 只要附加本技能并描述任务，就先进入选择环节 |
| 不限固定数量 | 罗列大概率用到的技能，兼顾主流程、辅助与替代方案 |
| 阶段与产物匹配 | 区分阅读、分析、起草、制图、排版、转换与检查等实际环节 |
| 当前会话优先 | 优先使用宿主提供的可用技能目录，保留插件命名空间 |
| 按需读取 | 元数据用于筛选，选定后才加载完整执行说明 |
| 本地只读盘点 | 可选标准库脚本支持中文和英文词面召回，不执行候选代码 |

## 快速开始

在 Codex 中选中 `skill-selector`，然后正常描述要做的任务即可。也可通过名称直接调用：

```text
$skill-selector 把这篇论文做成可编辑的组会汇报 PPT。
```

Agent 此时先给出各阶段所需技能、替代关系和建议组合，不直接解析整篇论文、写大纲或生成 PPT。你可以回复编号组合、技能名、“按建议组合”或“直接处理”；选定后再执行。普通的“帮我完成”不跳过选择环节。

也可以输入：

```text
使用本地技能选择器：我想分析这个 Excel 文件，只做分析，暂时不要制作报告。
```

没有合适技能时如实说明，不推荐虚构技能、不自动安装新技能。清单不只包含严格必需项，也包括大概率能参与这次任务的辅助技能和合理替代项；每项说明具体用途、使用条件与配合关系。不能为了简短而漏掉相关项，也不能把整个已安装目录无差别列出。建议组合只帮助选择，不替用户预先勾选。

## 安装与分发

**方式一：下载技能包。** 从 [dist/](dist/) 获取 `skill-selector-v0.1.2.zip`，解压后把顶层 `skill-selector` 文件夹放入宿主支持的技能目录。

**方式二：从 GitHub 安装到 Codex 用户目录。** 使用尚不存在的目标目录：

```bash
git clone https://github.com/Stephen-studying/SP_skill-dynamic_selector.git ~/.agents/skills/skill-selector
```

Windows PowerShell：

```powershell
git clone https://github.com/Stephen-studying/SP_skill-dynamic_selector.git "$env:USERPROFILE\.agents\skills\skill-selector"
```

仓库名是 `SP_skill-dynamic_selector`；**安装文件夹与调用名保持 `skill-selector`**。安装后查看宿主的技能列表，必要时刷新或新开会话。

安装包中的单个顶层文件夹是 `skill-selector/`，包含 `SKILL.md`、`agents/`、`scripts/`、`references/` 和 `LICENSE`。将它放入宿主支持的技能目录即可。

- Codex 项目安装：`<任务目录>/.agents/skills/skill-selector/`。
- Codex 用户安装：`~/.agents/skills/skill-selector/`；已有使用 `$CODEX_HOME/skills` 的环境也可以沿用其可发现目录。
- 其他 Agent：将同一份文件夹放入其支持的技能目录，使用该客户端实际支持的调用方式。

Codex 官方目录与调用机制见 [Build skills](https://learn.chatgpt.com/docs/build-skills)。平台差异、盘点参数与降级方式见 [references/platforms.md](references/platforms.md)。本项目的其他宿主适配为通用协议与目录预设，尚不代表已在所有客户端完成端到端验证。

开发者可以生成 ZIP，或安装到一个新的目录。已有目录中内容不同时，打包脚本会拒绝覆盖；更新前请自行检查差异。

```text
python scripts/package.py --output dist/skill-selector-v0.1.2.zip
python scripts/package.py --output dist/skill-selector-v0.1.2.zip --install /path/to/new/skills/skill-selector
```

此技能在被调用时运行，不会强制接管所有请求。没有自动更改用户的全局规则、插件配置或其他技能。

## Agent 兼容性

| 环境 | 使用方式 | 当前验证范围 |
| --- | --- | --- |
| Codex | 选中技能或通过 `$skill-selector` 调用 | 优先适配；格式、盘点、项目安装与文件一致性已验证 |
| Claude Code | 将完整文件夹放入其认可的技能目录 | 通用技能说明和目录预设；未做客户端端到端测试 |
| Gemini CLI | 将完整文件夹放入其认可的技能目录 | 通用技能说明和目录预设；未做客户端端到端测试 |
| 其他 Agent | 宿主需支持读取本地技能说明与多轮对话 | 使用宿主实际调用语法，不假设存在专用 `Skill` 工具 |

**Python 仅用于可选的盘点脚本。** Agent 已拿到技能目录时，可直接依据目录和文件工具筛选；没有 Python 也能使用说明流程。脚本不要求 API Key、第三方 Python 包或向量数据库。语义筛选由当前 Agent 完成。

## 本地优先与使用边界

- 盘点脚本不联网，不额外上传目录或维护远程索引；语义判断在当前 Agent 会话中完成，数据处理遵循宿主自身的隐私设置。不自动安装或启用新技能。
- “磁盘存在”与“当前宿主已启用”分开标记；不能把插件缓存当成已启用技能。
- 只有任务相关且有明确用途的候选才列入，不把整个安装目录无差别展示。
- 默认等待选择后执行；普通“帮我完成”不代表跳过选择。
- 被选中的下游技能可能需要联网、连接器或其他工具，其行为仍受用户任务与宿主权限约束。
- 不承诺固定推荐准确率，也不保证通过一个技能强制接管宿主全部请求。

## 实现与验证

- `SKILL.md`：任务理解、候选比较、等待选择、按选中技能执行。
- `scripts/inventory.py`：Python 3.11+ 标准库，只读扫描与可选词面召回。
- `agents/openai.yaml`：Codex UI 信息；隐式匹配保持宿主默认设置。
- `tests/`：盘点、中文处理、重复来源、禁用设置、循环目录及不执行候选代码等功能检查。

```text
python -m unittest discover -s tests -v
```

脚本测试不能证明 Agent 在任意任务上的推荐质量。真实宿主中还需检查以下行为：

| 场景 | 验收重点 |
| --- | --- |
| 选中本技能，只写“把论文做成 PPT” | 自动先给技能选择清单，无需出现“推荐技能” |
| 选中本技能，写“直接帮我完成” | 仍先展示清单；普通任务措辞不代表跳过选择 |
| 任务涉及多个互补阶段 | 清单覆盖全部必要技能，区分替代项和组合项 |
| 大概率用到的技能超过四个 | 全部罗列，包含相关辅助技能，不截断为前几名 |
| 论文 PDF → 可编辑 PPTX | 区分论文汇报、通用演示与 PDF 阅读技能，等选择再制作 |
| 公众号“目前只做选题” | 不提前写正文、配图、排版或发布 |
| 同名技能来自不同插件 | 保留来源和完整调用名 |
| 纯中文意译、描述只有英文 | Agent 进行语义判断，不把词面无匹配当作无技能 |
| 用户回复“2”，随后“继续” | 保留原任务与已选路线，完整读取选中说明 |
| 用户换任务或选中技能消失 | 重新核实，不静默换技能 |
| 用户仅请求推荐 | 回合停在选择环节，不执行目标任务 |
| 没有 Python 或专用技能调用工具 | 通过文件工具完成发现和加载，不编造工具调用 |

## 设计来源

根据本项目需求独立编写。前期调研参考了 [pcx-wave/skill-router](https://github.com/pcx-wave/skill-router) 的候选选择交互、[MMStudioCreations/skill-router](https://github.com/MMStudioCreations/skill-router) 的动态盘点思路，以及 Codex 官方技能格式；没有复制这些项目的实现。

原创代码、技能说明与矢量视觉采用 [MIT License](LICENSE)。被选择的其他技能、示例中提及的产品和第三方工具各遵循其自身许可。

---

<div align="center">

**先看见可用能力，再决定怎样完成任务。**

[阅读技能说明](SKILL.md) · [下载技能包](dist/) · [反馈问题](https://github.com/Stephen-studying/SP_skill-dynamic_selector/issues)

</div>
