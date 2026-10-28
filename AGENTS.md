# TranslationHub 项目规范

仓库唯一的流程规范源：命令、文件角色、编码与提交规则。翻译风格与术语见 skills。

## 门禁

按顺序执行，任一非零退出码即失败。

```bash
uv run check_all.py                          # 全仓库：4 个自检 → bdd --check → sync → build → verify
uv run sync_translation.py <name> --check    # 单模组：缺键 + 英文基线变更
uv run build_all.py --dry-run <name>
uv run build_all.py <name1> <name2>
uv run verify_translation.py <name>
```

`<name>` 接受 `mods.toml` 的完整 `dir` 或目录 basename；未知名称和验证错误都返回非零。
`verify_translation.py` 覆盖已登记模组、eslifer 和 descriptionmods。

## 文件角色与路由

| 文件类型 | 可编辑源 | 产物 | 路径与技能 |
|---|---|---|---|
| `mods.toml` 的 line / json / qt | 模组目录内 `translations.json` | 配置生成的 TXT/INI/JSON/TS | 任意模组目录，`translation-io` + `game-translation` |
| xTranslator XML | `pending.json` | XML 的 `TRADUIT` 字段 | `dialogue_mod_translation/`，`dialogue-xml` + `game-translation` |
| Description 文件 | `descriptionmods/translations.json` | `descriptionmods/zh/...` | `translation-io` + `game-translation` |
| Qt TS | `eslifer/translations.json` | `eslifer/eslifier_translation.ts` | 共用 `qt` 处理器 |
| 新类型或未知文件 | — | — | `translation-io` 先做准入，再按类型处理 |

除 Dialogue XML 外，所有模组以 `translations.json` 为唯一可编辑源，禁止直接编辑产物。
英文源只读，只在同步上游版本时修改。Dialogue XML 不登记在 `mods.toml`。
line/json 模组目录下的 `.translations.source.json` 是英文基线，由 `sync_translation.py` 维护并提交，不要手改；
Qt TS 不用基线，因为源文本本身就是键。

目录名小写、不含空格，多词用连字符连接（如 `input-manager`、`npc-stats-editor`、`dodge-for-all`）。
模组目录名只用于仓库内部和 `dist/<name>`，不影响游戏路径；游戏路径由 `source` / `output` 决定。
`menu_translation/` 同时容纳 MCM 与 SKSE Menu Framework 两类配置菜单，走哪条构建路径只由
`mods.toml` 的 `line` / `json` 条目决定，不要按目录名推断。换框架时改 `source` / `output` / `sep` / `encoding`，目录不必动。

## 添加模组

在 `mods.toml` 添加 `[[line]]` / `[[json]]`，Qt TS 用共用的 `[[qt]]`。不要在模组目录加脚本，
也不要在 Python 里维护模组列表。

```toml
[[line]]
dir = "path/to/mod"
source = "source.txt"
output = "target.txt"
sep = "\\t"
encoding = "utf16-le-bom"
```

首次启用后先 `uv run sync_translation.py --all --accept-source`（或对单模组运行）并提交基线，
再 `--dry-run`、构建、验证。

`--check` 发现已翻译键的英文原文变化返回 `[变更]`，没有基线返回 `[未基线]`，两者都非零。
`--sync` 补缺失键并把新键写入基线，但不接受已有键的英文变更；`--accept-source` 只更新基线，不动 `translations.json`。

## Dialogue XML

按 `.agents/skills/dialogue-xml/SKILL.md` 执行，顺序为 `stats → pending --fill-bdd → apply → stats`。
词典 `bdd.tsv` 是带引号的 TSV，字段可跨行；只能用 `translate.py bdd` 维护，不要手工按行拆。

## 打包

```bash
uv run package.py <name>              # 构建 + dist/<name>/ 与 dist/<name>.7z
uv run package.py <name> --list       # 只看打包计划，不执行
uv run package.py --all --no-archive  # 全量，只生成目录
```

落点由 `mods.toml` 的 `package` 字段决定，可写多个。未写时按 `output` 推导：
`output` 带 `interface/` 或 `SKSE/` 前缀则直接沿用，否则拼 `interface/translations/` 并警告。

模组目录默认把工作目录做成游戏结构，`source` / `output` / `package` 三者路径一致，不用再手写 `package`：

```text
menu_translation/<mod>/
  interface/translations/X_english.txt      ← source
  interface/translations/X_chinese.txt      ← output
  SKSE/Plugins/<plugin>/Y_EN.txt            ← source
  SKSE/Plugins/<plugin>/Y_ZH.txt            ← output
```

玩家可能跑英文环境（读 `*_english.*` / `*_EN.*`）或中文环境（读 `*_chinese.*` / `*_ZH.*`）。
`interface/translations/` 下两种文件名都打包；`SKSE/Plugins/` 下只打英文名，
插件按固定文件名读取，中文名放进去不会被加载。内容都是中文。`dist/` 已在 `.gitignore` 中。

## 代码约定

- 所有 CLI 走 `config.setup_cli_logging`：一个 UTF-8 stdout handler，默认 INFO，`--verbose` 时 DEBUG。
  只用具名 logger；`print` 只用于表格、摘要和用户提示；不要打印 `translations.json` 的值。
- 门禁判断依赖退出码，不依赖输出文本。

## 翻译约束

- 术语优先级：模组术语表/档案 > 附近已有译文 > `bdd.tsv`（Dialogue XML）> 游戏既有译名。
- 占位符必须与源文件逐条对齐：`%s`、`%llu`、`%1`、`{0}`、`$VAR$`、`<font>`、`[br]`、字面量 `\n`。
  漏一个就可能让游戏崩溃或显示错乱。
- 只改翻译源，不改生成产物；改动写入仓库文件，不要在对话里返回只有译文的转储。

## 提交与推送

改动通过检查后创建提交并推送到当前分支跟踪的远端。只暂存本次相关文件，保留无关的工作区改动。
禁止强制推送；远端已分叉时先检查并整合，不要重写已发布的历史再推送。
