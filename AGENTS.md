# TranslationHub 项目规范

英文源文件是全部输入，`translations.json` 是唯一可编辑源；产物与英文源只读，
`.translations.source.json` 由 `sync_translation.py` 维护。风格见 `game-translation`，
字段、编码与 `upstream` 见 `translation-io`。

## 翻译一个模组

`<name>` = `mods.toml` 的 `dir` 或目录 basename；类型只由 `mods.toml` 条目决定。

```bash
uv run sync_translation.py <name> --check       # 已有：缺键 / 原文变更 / 无基线，命中非零
uv run sync_translation.py <name> --sync --yes  # 新模组：生成英文骨架（缺键未补齐不写基线）
uv run build_all.py <name> && uv run verify_translation.py <name>
uv run package.py <name>                        # dist/ + 部署到 MO2 汉化目录
```

| 源 | 只改这里 |
|---|---|
| line / json / qt | 模组目录 `translations.json`（qt 源文本即键，无基线） |
| Description | `descriptionmods/translations.json` |

上游改文案：`--check` → `--changed` 核对 → `--sync` 补新键 → `--accept-source` 接受新英文；
`--changed` 不能与其他写命令同用。新模组在 `mods.toml` 加 `[[line]]` / `[[json]]` / `[[qt]]`，
不要在模组目录放脚本，不要在 Python 里维护模组列表，字段白名单见 `translation-io`。
专有名词查全局表 `bdd.tsv`（grup / original / traduit，只读）：`rg -N "\tX\t" bdd.tsv`。

## 提交前

`uv run check_all.py`（全量：空目录 → 自检 → sync → build → verify → package --list）退出码 0 才提交。
只暂存本次相关文件；禁止强推，远端正分叉先整合。

## 打包与部署

落点取 `mods.toml` 的 `package`；未写时按 `output` 推导：带 `interface/` / `SKSE/` 前缀沿用，
否则拼 `interface/translations/`。`interface/translations/` 英中同名都打，`SKSE/Plugins/`
只打英文名（内容都是中文）；插件自解析文本（如 dMenu 的 `translations.txt`）产物加 `_zh`，
`package` 写回源文件名。更新译文后必须重跑 `package.py`；`dist/` 不入库；`[[qt]]` 配了 `qm` 时打包 qm。

部署默认把 `dist/<name>/` 覆盖到由 `upstream` 推导的 `<目录> 汉化`（或 `和光汉化`），
例外写 `deploy = "<目录名>"` / `deploy = false`，推不出且没写报错退出（`--list` 只警告）。

## 约定

目录名小写连字符；`menu_translation/` 下 MCM 与 SKSE Menu Framework 的区别只看 `mods.toml` 条目，
换框架只改路径与字段，目录不动。CLI 走 `config.setup_cli_logging`，`print` 只用于表格，
不打印译文值（`--changed` 除外）。
