# TranslationHub 项目规范

本文件是仓库唯一的流程规范源。命令、文件角色、准入要求、编码与提交规则都写在这里。

## 门禁

按顺序执行，任一非零退出码即失败。

```bash
uv run check_all.py                          # 全仓库一次性门禁
uv run sync_translation.py <name> --check    # 单模组
uv run build_all.py --dry-run <name>
uv run build_all.py <name1> <name2>
uv run verify_translation.py <name>
```

`check_all.py` 按 gate 顺序一次跑完：四个脚本的自检 → `bdd --check` → sync → build → verify，共 8 步。
单模组用上面四条命令。`verify_translation.py` 覆盖已登记模组、Eslifer 和 Descriptionmods。
`<name>` 接受 `mods.toml` 中的完整 `dir` 或目录 basename；未知名称和验证错误都返回非零退出码。

## 文件角色与路由

| 文件类型 | 可编辑源 | 产物 / 目标 | 路径与所需技能 |
|---|---|---|---|
| `mods.toml` 的 line / json / qt | 模组目录内 `translations.json` | 配置生成的 TXT/INI/JSON/TS | 任意模组目录，`translation-io` + `game-translation` |
| xTranslator XML | `pending.json` | XML 的 `TRADUIT` 字段 | `dialogue_mod_translation/`，`dialogue-xml` + `game-translation` |
| Description 文件 | `Descriptionmods/translations.json` | `Descriptionmods/zh/...` | `translation-io` + `game-translation` |
| Qt TS | `Eslifer/translations.json` | `Eslifer/eslifier_translation.ts` | 共用 `qt` 处理器 |
| 新类型或未知文件 | — | — | `translation-io` 先做准入，再按类型处理 |
| 任意游戏文本 | — | — | `game-translation` |

除 `dialogue_mod_translation/` 外，所有模组都以 `translations.json` 为唯一可编辑源。
禁止直接编辑构建产物。英文源默认只读，只在同步上游版本时修改。Dialogue XML 不登记在 `mods.toml`。

## 日常流程

```bash
# 1. 检查上游是否新增行文本键
uv run sync_translation.py <mod> --check

# 2. 编辑 translations.json 后构建
uv run build_all.py <mod>

# 3. 验证键覆盖、未使用键、占位符、转义和产物是否最新
uv run verify_translation.py <mod>
```

Dialogue XML 用 `translate.py`，顺序为 `stats → pending --fill-bdd → apply → stats`。

## 新模组准入

翻译新模组前先检查目录，逐个判定候选源文件和目标文件的类型。不要只按扩展名推断类型或编码。

1. 用 `rg --files <mod-dir>` 列出文件。压缩包和二进制文件不参与文本解析。
2. 对可能的文本文件先检测再解码：

```bash
uv run locale_utils.py detect <file>
uv run locale_utils.py dump <file>
```

`detect` 只检查 BOM。无 BOM 文件由 `dump` 按 UTF-8 严格解码。
解码失败时不要试探其他编码，应停止并询问源编码。解码成功也不能证明原编码。还要核对模组说明和配对文件。

3. 检查文件结构并对比源/目标样本。JSON 和 XML 必须按结构解析。
   确认键、分隔符、注释和行尾。角色未确认前不要编辑或构建。
4. 如果类型、源、目标或输出编码任一不清楚，停止并询问。不要猜编码，不要编辑或构建未分类的文件。
5. 在 `mods.toml` 登记为 `line`、`json` 或 `qt`。Dialogue XML 流程保持独立。
   从确认的源键创建并翻译 `translations.json`。运行 `uv run build_all.py --dry-run <mod>`，再构建和验证。

## 添加配置模组

在 `mods.toml` 添加 `[[line]]` 或 `[[json]]`，共用构建器处理所有此类模组。
Qt TS 使用仓库共用的 `[[qt]]` 处理器。不要在模组目录中添加脚本，也不要在 Python 脚本里维护模组列表。

```toml
[[line]]
dir = "path/to/mod"
source = "source.txt"
output = "target.txt"
sep = "\\t"
encoding = "utf16-le-bom"

[[json]]
dir = "path/to/mod"
source = "source.json"
output = "target.json"
```

## 编码与格式

编码、分隔符和输出文件名以 `mods.toml` 为准。保留键、节、顺序、分隔符、注释、数字、行结构和格式。
占位符包括 `%s`、`%llu`、`%1`、`{0}`、`$VAR$`、`<font>`、`[br]` 和字面量 `\n`。

## 特殊类型

- Dialogue XML：按 `.agents/skills/dialogue-xml/SKILL.md` 执行，顺序为 `stats → pending → apply → stats → --self-check`。
  词典 `bdd.tsv` 是带引号的 TSV，字段可跨行；只能用 `translate.py bdd` 子命令维护，不要手工按行拆。
- Descriptionmods：编辑 `Descriptionmods/translations.json`，运行 `uv run build_all.py Descriptionmods`，再运行对应验证命令。
- Qt TS：编辑 `Eslifer/translations.json`，运行 `uv run build_all.py Eslifer`，再运行对应验证命令。
- 全量验证覆盖所有已登记模组、Eslifer 和 Descriptionmods。

## 术语与风格

- 术语优先级：模组术语表/档案 > 附近已有译文 > `bdd.tsv`（Dialogue XML）> 游戏既有译名。
- `perk` 默认保留英文，只有游戏语境需要本地化术语时才翻译。
- 只改翻译源，不改生成产物。
- 改动写入仓库文件，不要在对话里返回只有译文的转储。

## Python 与依赖

本项目由 uv 管理，非打包项目。要求 Python 3.11+，运行时只用标准库。

- 直接用 `uv run <script.py>` 运行仓库脚本。不要在 `uv run` 和脚本路径之间加 `python`。
- 优先使用标准库。能不用第三方包就不要装。
- 长期运行时依赖用 `uv add <package>`，仅开发用工具用 `uv add --dev <package>`。`pyproject.toml` 和 `uv.lock` 都要提交。
- 依赖变更后用 `uv sync` 同步本地 `.venv`；不能修改 lockfile 的检查用 `uv sync --locked`。
- 一次性脚本用 `uv run --with <package> --script <script.py>`，独立 CLI 工具用 `uvx <tool>`。
- 禁止用 `pip` 安装包，禁止改动全局 Python 环境。

## 日志

所有 CLI 都走 `config.setup_cli_logging`：

- 一个 UTF-8 stdout handler。默认 INFO，`--verbose` 时 DEBUG。
- 只用具名 logger：`log = logging.getLogger(__name__)`。
- `print` 只用于表格、摘要和用户提示。
- 不要打印 `translations.json` 的值。门禁判断依赖退出码，不依赖输出文本。

## 提交与推送

完成一次仓库改动并通过检查后，创建提交并推送到当前分支跟踪的远端。
只暂存与本次工作相关的文件，保留无关的工作区改动。禁止强制推送。
如果远端已分叉，先检查并整合其改动，不要重写已发布的历史再推送。
