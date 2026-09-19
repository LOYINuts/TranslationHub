---
name: translation-io
description: Read and write Skyrim translation TXT/INI files safely, including UTF-16 BOM and UTF-8. Use for *_translation directories and Descriptionmods.
---

# 翻译文件读写

## First Decision

1. If directory has `translations.json`, edit only that file; output TXT/INI/JSON is generated.
2. Under `Descriptionmods/`, edit matching `Descriptionmods/zh/...` file directly.
3. Otherwise edit Chinese TXT/INI directly.

## Encoding

Before direct TXT/INI edits:

```bash
python locale_utils.py detect PATH
python locale_utils.py dump PATH
```

Do not use Pi `read` for UTF-16 files. For direct writes, use `locale_utils.write_utf16le_bom`, `write_utf8_bom`, or `write_utf8`; preserve existing encoding and newline convention.

## Configured Mods

```bash
python sync_translation.py <name> --check
python sync_translation.py <name> --sync
python build_all.py --dry-run <name>
python build_all.py <name>
python verify_translation.py <name>
```

Separator and encoding come from `mods.toml`; never infer a global `=` spacing rule. Preserve keys, sections, ordering, comments, placeholders, tags, escaped `\\n`, and other nontranslated fields.

For `Descriptionmods`, preserve each `key|description|metadata...` record and verify with:

```bash
python verify_translation.py Descriptionmods
```

Any nonzero exit means incomplete work.
