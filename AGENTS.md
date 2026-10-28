# TranslationHub 项目规范

命令、文件角色、编码与提交规则的唯一来源。翻译风格见 `game-translation`，文件读写与新模组准入见
`translation-io`，XML 见 `dialogue-xml`（都在 `.agents/skills/`，按需加载）。

## 门禁

任一非零退出码即失败，只看退出码。

```bash
uv run check_all.py                         # 全量：空目录 → 自检 → bdd --check → sync → build → verify
uv run sync_translation.py <name> --check   # 缺键 / 原文变更 / 无基线，命中都非零
uv run sync_translation.py <name> --changed # 逐条列出原文变更的键与现译文，只读
uv run build_all.py --dry-run <name>
uv run build_all.py <name>
uv run verify_translation.py <name>
```

`<name>` 用 `mods.toml` 的 `dir` 或目录 basename。

上游改文案后：`--check` 看有几条 `[变更]` → `--changed` 逐条核对并改 `translations.json` →
`--sync` 补新键 → 译新键 → `--accept-source` 让基线接受新英文 → build → verify。
`--sync` 不接受已有键的英文变更，`--accept-source` 不动 `translations.json`；`--changed` 不能与其他写命令同用。

## 文件角色

| 类型 | 唯一可编辑源 | 产物 |
|---|---|---|
| line / json / qt | 模组目录 `translations.json` | 配置生成的 TXT/INI/JSON/TS |
| xTranslator XML | `pending.json` | XML 的 `TRADUIT`，STATUS 记 `90` |
| Description | `descriptionmods/translations.json` | 同目录 `*_zh.ini` |

产物与英文源只读；`.translations.source.json` 由 `sync_translation.py` 维护，不手改。
Dialogue XML 不登记 `mods.toml`；Qt TS 不用基线，源文本即键。
目录名小写、无空格、多词连字符（`input-manager`）。游戏路径只由 `source` / `output` / `package` 决定；
`menu_translation/` 下 MCM 与 SKSE Menu Framework 的区别只看 `mods.toml` 条目，不按目录名推断，
换框架只改路径与字段，目录不动。

## 加模组

`mods.toml` 加 `[[line]]` / `[[json]]` / `[[qt]]`；不要在模组目录放脚本，不要在 Python 里维护模组列表。
字段白名单（`sep`、`encoding`、`output_sep`、`value_field`、`translation_section`、glob 键格式）见 `translation-io`。
首次启用后 `uv run sync_translation.py --all --accept-source` 并提交基线，再 `--dry-run`、build、verify。

## Dialogue XML

顺序 `stats → pending --fill-bdd → apply → stats`：

```bash
uv run dialogue_mod_translation/translate.py stats <xml>
uv run dialogue_mod_translation/translate.py pending <xml> --fill-bdd
uv run dialogue_mod_translation/translate.py apply <mod>/pending.json
```

`bdd.tsv` 是带引号的 TSV，字段可跨行，只用 `translate.py bdd` 维护。

## 打包

```bash
uv run package.py <name>              # 构建 + dist/<name>/ 与 dist/<name>.7z
uv run package.py <name> --list       # 只看计划
uv run package.py --all --no-archive  # 全量，只出目录
```

落点取 `mods.toml` 的 `package`（可多个）；未写时按 `output` 推导：带 `interface/` / `SKSE/` 前缀直接沿用，
否则拼 `interface/translations/` 并警告。`interface/translations/` 的英文名与中文名都打包，
`SKSE/Plugins/` 只打英文名（插件按固定名读）；两种内容都是中文。

## 翻译约束

- 术语优先级：本模组既有译文 > 相邻模组同名词 > `bdd.tsv` > 游戏既有译名。
- 占位符与标记逐条对齐：`%s`、`%llu`、`%1`、`{0}`、`$VAR$`、`<font>`、`[br]`、字面量 `\n`。
- 只改翻译源，改动写进仓库文件，不在对话里返回纯译文转储；`translations.json` 就地增改，不整表重排或重格式化。

## 代码约定

CLI 一律走 `config.setup_cli_logging`（UTF-8 stdout，`--verbose` 转 DEBUG），用具名 logger；
`print` 只用于表格与用户提示，不打印 `translations.json` 的值（`--changed` 除外）。

## 提交

检查全过后提交并推送到当前分支跟踪的远端。只暂存本次相关文件，保留无关改动；禁止强推，远端正分叉时先整合。
