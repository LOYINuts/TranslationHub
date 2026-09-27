---
name: translation-io
description: Inspect and process translation text files safely, including UTF-16 BOM and UTF-8, in configured or new mod folders.
---

# 翻译文件读写

## First Decision

1. For configured mods, edit only `translations.json`. Build the output files.
2. For `Descriptionmods`, edit `Descriptionmods/translations.json`, then run
   `python build_all.py Descriptionmods`.

## 新目录或未配置目录

1. 用 `rg --files <mod-dir>` 列出文件。确认编码前，不要用 Pi `read` 打开文件。
2. 对可能的文本文件运行：
   `python locale_utils.py detect PATH`
   `python locale_utils.py dump PATH`
3. `detect` 只检查 BOM。`dump` 按 UTF-8 严格解码无 BOM 文件。
   解码成功也不能证明原编码。
4. 检查文件结构并对比源文件和目标文件。JSON 和 XML 必须按结构解析。
5. 若编码、文件类型、源/目标角色或输出编码不清楚，停止并询问。
   不要试探其他编码，也不要为让解析成功而改源文件。
6. 在 `mods.toml` 中登记 `line`、`json` 或 `qt` 类型。Dialogue XML 流程保持独立。
7. 根据已确认的源键创建并翻译 `translations.json`。
   运行 `python build_all.py --dry-run <mod>`，再构建和验证。

## Encoding

Read source encoding before you inspect TXT/INI files:

```bash
python locale_utils.py detect PATH
python locale_utils.py dump PATH
```

Do not use Pi `read` for UTF-16 files. Generated output keeps the source
encoding and newline convention. Use `build_all.py` to make output files.

## Configured Mods

```bash
python sync_translation.py <name> --check
python sync_translation.py <name> --sync
python build_all.py --dry-run <name>
python build_all.py <name>
python verify_translation.py <name>
```

Separator and encoding come from `mods.toml`. Do not infer a global `=` rule.
Preserve keys, sections, order, comments, placeholders, tags, escaped `\\n`,
and other nontranslated fields.

For `Descriptionmods`, preserve every `key|description|metadata...` record.
Build and verify it with:

```bash
python build_all.py Descriptionmods
python verify_translation.py Descriptionmods
```

Any nonzero exit means incomplete work.
